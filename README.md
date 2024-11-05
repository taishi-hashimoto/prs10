# prs10

A python package for commanding and monitoring the Rubidium Frequency Standard PRS10 by Stanford Research Systems.

- [PRS10 - Stanford Research Systems](https://www.thinksrs.com/products/prs10.html)

## Install

Use pip:

```bash
pip install .
```

## Usage

### `prs10d`

`prs10d` is designed to be run as a daemon.  
It communicates with PRS10 and periodically read the current status and send to zmq PUB socket.

```
$ prs10d --help
usage: prs10d [-h] [path_yaml]

Periodically query the current status of Rubidium Frequency Standard Model PRS10.

positional arguments:
  path_yaml   Path to YAML configuration file.

options:
  -h, --help  show this help message and exit
```

### `prs10`

**NOTE: to use `prs10`, make sure that `prs10d` is running.**

`prs10` is a tool that send command to `prs10d` and receive output.  
This tool cannot be used when `prs10d` is not running.


```
$ prs10 --help
usage: prs10 [-h] [-a] [-c [COMMAND ...]] [path_yaml]

Commanding and monitoring tool for the Rubidium Frequency Standard Model PRS10.

positional arguments:
  path_yaml             Path to YAML configuration file.

options:
  -h, --help            show this help message and exit
  -a, --all
  -c [COMMAND ...], --command [COMMAND ...]
```

Example output:

```
$ prs10
DEVICE ID  : PRS10_3.56_SN_107831
SERIAL NO. : 107831
CASE TEMP. : 70.30 ℃
IS LOCKED? : True
STATUS BITS:
  00000000 ST1: Power supplies and Discharge Lamp
  00000000 ST2: RF Synthesizer
  00000000 ST3: Temperature Controllers
  00000000 ST4: Frequency Lock-Loop Control
  10000100 ST5: Frequency Lock to External 1pps
  │    └─────── PLL restarted                    Provide stable 1pps inputs
  └──────────── PLL disabled                     Send PL 1 to enable
  00000000 ST6: System Level Events
```

### `prs10stat`

NOTE: to use `prs10stat`, make sure that `prs10d` is **not** running.

```
$ prs10stat -h
usage: prs10stat [-h] [-a] [-c COMMAND [COMMAND ...]] [device]

Get the current status of the Rubidium Frequency Standard Model PRS10.

positional arguments:
  device                Serial device where the RS-232C port of PRS10 is mounted. Default is `/dev/ttyUSB0`.

options:
  -h, --help            show this help message and exit
  -a, --all             Show all status bits.
  -c COMMAND [COMMAND ...], --command COMMAND [COMMAND ...]
                        Send a command.
```

Example output:

```bash
$ prs10stat /dev/ttyUSB0
```

```
DEVICE ID  : PRS10_3.56_SN_107831
SERIAL NO. : 107831
CASE TEMP. : 69.60 ℃
IS LOCKED? : True
STATUS BITS:
  00000000 ST1: Power supplies and Discharge Lamp
  00000000 ST2: RF Synthesizer
  00000000 ST3: Temperature Controllers
  00000000 ST4: Frequency Lock-Loop Control
  10000100 ST5: Frequency Lock to External 1pps
  │    └─────── PLL restarted                    Provide stable 1pps inputs
  └──────────── PLL disabled                     Send PL 1 to enable
  00000000 ST6: System Level Events
```

### In Python

Below code generates a similar output with `prs10stat /dev/ttyUSB0` above:

```python
from prs10 import PRS10

with PRS10("/dev/ttyUSB0") as rb:
    print("DEVICE ID  :", rb.id)
    print("SERIAL NO. :", rb.serial_number)
    print(f"CASE TEMP. : {rb.case_temperature:.2f} ℃")
    print("IS LOCKED? :", rb.is_locked)
    print("STATUS BITS:")
    print(rb.status.to_str(indent=2, compress=True))
```
