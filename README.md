# prs10

A python package for commanding and monitoring the Rubidium Frequency Standard PRS10 by Stanford Research Systems.

- [PRS10 - Stanford Research Systems](https://www.thinksrs.com/products/prs10.html)

## Install

Use pip:

```bash
pip install .
```

## Usage

### From terminal

Use `prs10stat`:

```bash
$ prs10stat --help
```

```
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
