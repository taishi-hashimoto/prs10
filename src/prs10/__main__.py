import zmq
import time
import yaml
from os.path import expanduser
from datetime import datetime, timedelta
from argparse import ArgumentParser
from . import PRS10


def prs10stat():
    argp = ArgumentParser(
        description="Get the current status of the Rubidium Frequency Standard Model PRS10.",
        epilog="NOTE: This program should not be used when `prs10d` is running. Either stop `prs10d` or use `prs10` instead."
    )
    argp.add_argument(
        "device",
        help="Serial device where the RS-232C port of PRS10 is mounted. Default is `/dev/ttyUSB0`.",
        nargs="?",
        default="/dev/ttyUSB0"
    )
    argp.add_argument(
        "-a", "--all", action="store_true",
        help="Show all status bits."
    )
    argp.add_argument(
        "-c", "--command", type=str,
        help="Send a command.",
        nargs="+",
        default=None
    )
    args = argp.parse_args()

    with PRS10(args.device) as prs10:
        if args.command is None:
            print("DEVICE ID  :", prs10.id)
            print("SERIAL NO. :", prs10.serial_number)
            print(f"CASE TEMP. : {prs10.case_temperature:.2f} ℃")
            print("IS LOCKED? :", prs10.is_locked)
            print("STATUS BITS:")
            print(prs10.status.to_str(indent=2, compress=not args.all))
        else:
            prs10.timeout = 0.1
            ans = prs10.write(" ".join(args.command)).read()
            if ans:
                print(ans)


DEFAULT_CONFIG = expanduser("~/.prs10/prs10.yaml")

def prs10d():
    argp = ArgumentParser(
        description="Periodically query the current status of Rubidium Frequency Standard Model PRS10."
    )
    argp.add_argument(
        "path_yaml",
        help="Path to YAML configuration file.",
        nargs="?",
        default=DEFAULT_CONFIG
    )
    args = argp.parse_args()
    with open(args.path_yaml) as f:
        conf = yaml.safe_load(f)
    ctx = zmq.Context.instance()
    sock: zmq.Socket = ctx.socket(zmq.PUB)
    sock.bind(conf["mq_pub"])
    sock_in: zmq.Socket = ctx.socket(zmq.REP)
    sock_in.bind(conf["mq_cmd"])

    interval = timedelta(**conf["interval"])
        
    with PRS10(conf["device"], conf["timeout"]) as prs10:
        prev = now = datetime.now()
        while True:
            try:
                now = datetime.now()
                try:
                    cmd = sock_in.recv_string(zmq.NOBLOCK)
                    ans = prs10.write(cmd).read()
                    sock_in.send_string(ans, zmq.DONTWAIT)
                except zmq.ZMQError:
                    pass
                if now - prev < interval:
                    time.sleep(0.1)
                else:
                    sock.send_json({
                        "lock": prs10.is_locked,
                        "temp": prs10.case_temperature,
                        "status": prs10.status.raw
                    })
                    prev = now
            except KeyboardInterrupt:
                break


def prs10():
    argp = ArgumentParser(
        description="Commanding and monitoring tool for the Rubidium Frequency Standard Model PRS10.",
    )
    argp.add_argument(
        "path_yaml",
        help="Path to YAML configuration file.",
        nargs="?",
        default=DEFAULT_CONFIG
    )
    argp.add_argument("-a", "--all", action="store_true")
    argp.add_argument("-c", "--command", type=str, nargs="*", default=None)
    args = argp.parse_args()
    with open(args.path_yaml) as f:
        conf = yaml.safe_load(f)
    
    ctx = zmq.Context.instance()
    sock_in: zmq.Socket = ctx.socket(zmq.REQ)
    sock_in.connect(conf["mq_cmd"])
    if args.command is None:
        sock_in.send_string("ID?")
        id = sock_in.recv_string()
        sock_in.send_string("SN?")
        sn = sock_in.recv_string()
        sock_in.send_string("AD10?")
        temp = float(sock_in.recv_string())*100
        sock_in.send_string("LO?")
        is_locked = sock_in.recv_string() == "1"
        sock_in.send_string("ST?")
        status = PRS10.StatusBytes(sock_in.recv_string())
    
        print("DEVICE ID  :", id)
        print("SERIAL NO. :", sn)
        print(f"CASE TEMP. : {temp:.2f} ℃")
        print("IS LOCKED? :", is_locked)
        print("STATUS BITS:")
        print(status.to_str(indent=2, compress=not args.all))
    else:
        command = " ".join(args.command)
        sock_in.send_string(command)
        print(sock_in.recv_string())
