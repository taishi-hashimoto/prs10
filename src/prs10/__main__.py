from argparse import ArgumentParser
from . import PRS10


def prs10stat():
    argp = ArgumentParser(
        description="Get the current status of the Rubidium Frequency Standard Model PRS10."
    )
    argp.add_argument(
        "device",
        help="Serial device where the RS-232C port of PRS10 is mounted. Default is `/dev/ttyUSB0`.",
        nargs="?",
        default="/dev/ttyUSB0"
    )
    argp.add_argument(
        "--full", action="store_true",
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
            print(prs10.status.to_str(indent=2, compress=not args.full))
        else:
            prs10.timeout = 0.1
            ans = prs10.write(" ".join(args.command)).read()
            if ans:
                print(ans)
