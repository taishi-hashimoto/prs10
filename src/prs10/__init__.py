"Commanding and monitoring library for the Rubidium Frequency Standard Model by Stanford Research Systems."

import io
import serial


class PRS10:
    "Rubidium Frequency Standard Model PRS10 by Stanford Research Systems"

    def __init__(self, device: str):
        """"""
        self._device = device
        self._s = None

    def __enter__(self):
        self.open(self._device)
        return self

    def __exit__(self, ex_type, ex_value, trace):
        self.close()

    def open(self, device):
        self._device = device
        self._s = serial.Serial(
            port=device,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            xonxoff=True
        )

    def close(self):
        self._s.close()

    def write(self, command: str) -> 'PRS10':
        self._s.write(command.encode() + serial.CR)
        return self

    def read(self) -> str:
        return self._s.read_until(serial.CR).rstrip(serial.CR).decode()

    @property
    def id(self) -> str:
        "Identifier of this instrument."
        self.write("ID?")
        return self.read()

    @property
    def serial_number(self) -> str:
        "Serial number of this instrument."
        self.write("SN?")
        return self.read()

    @property
    def is_locked(self) -> bool:
        "Return `True` if the frequency lock loop is locked."
        self.write("LO?")
        return self.read() == "1"

    @property
    def case_temperature(self) -> float:
        """Return the case temperature in degrees Celcius.
        
        NOTE:AD10?: Case temperature (10 mV/℃).
            This sensor indicates a temperature which is about midway between
            the baseplate temperature and the lamp temperature.
        """
        return float(self.write("AD10?").read()) * 100

    @property
    def status(self) -> 'StatusBytes':
        """Status bytes by `ST?` command.
        
        NOTE: A status bit will remained set until it is read, even though
              the condition which caused the error has been removed.
        """

        return self.StatusBytes(self.write("ST?").read())

    class StatusBytes:
        "Status Bytes returned by ST? command."

        BYTES = [
            "ST1: Power supplies and Discharge Lamp",
            "ST2: RF Synthesizer",
            "ST3: Temperature Controllers",
            "ST4: Frequency Lock-Loop Control",
            "ST5: Frequency Lock to External 1pps",
            "ST6: System Level Events"
        ]

        CONDITIONS = [
            [  # ST1
                "+24 for electronics < +22 Vdc",
                "+24 for electronics > +30 Vdc",
                "+24 for heaters < +22 Vdc",
                "+24 for heaters > +30 Vdc",
                "Lamp light level too low",
                "Lamp light level too high",
                "Gate voltage too low",
                "Gate voltage too high"
            ],
            [  # ST2
                "RF synthesizer PLL unlocked",
                "RF crystal varactor too low",
                "RF crystal varactor too high",
                "RF VCO control too low",
                "RF VCO control too high",
                "RF AGC control too low",
                "RF AGC control too high",
                "Bad PLL parameter"
            ],
            [  # ST3
                "Lamp temp below set point",
                "Lamp temp above set point",
                "Crystal temp below set point",
                "Crystal temp above set point",
                "Cell temp below set point",
                "Cell temp above set point",
                "Case temperature too low",
                "Case temperature too high"
            ],
            [  # ST4
                "Frequency lock control is off",
                "Frequency lock is disabled",
                "10 MHz EFC is too high",
                "10 MHz EFC is too low",
                "Analog cal voltage  > 4.9 V",
                "Analog cal voltage < 0.1",
                "",
                ""
            ],
            [  # ST5
                "PLL disabled",
                "< 256 good 1pps inputs",
                "PLL active",
                "> 256 bad 1pps inputs",
                "Excessive time interval",
                "PLL restarted",
                "f control saturated",
                "No 1pps input"
            ],
            [  # ST6
                "Lamp restart",
                "Watchdog time-out and reset",
                "Bad interrupt vector",
                "EEPROM write failure",
                "EEPROM data corruption",
                "Bad command syntax",
                "Bad command parameter",
                "Unit has been reset"
            ]
        ]

        CORRECTIVE_ACTIONS = [
            [  # ST1
                "Increase supply voltage",
                "Decrease supply voltage",
                "Increase supply voltage",
                "Decrease supply voltage",
                "Wait: check SD2 setting",
                "Check SD2 setting",
                "Wait: check SD2 setting",
                "Check SD2 setting"
            ],
            [  # ST2
                "Query SP? verify values",
                "Query SP? verify values",
                "Query SP? verify values",
                "Query SP? verify values",
                "Query SP? verify values",
                "Check SD0? values",
                "Check SD0? values",
                "Query SP? verify values"
            ],
            [  # ST3
                "Wait for warm-up",
                "Check SD3, ambient",
                "Wait for warm-up",
                "Check SD4, ambient",
                "Wait for warm-up",
                "Check SD5, ambient",
                "Wait for warm-up",
                "Reduce ambient"
            ],
            [  # ST4
                "Wait for warm-up",
                "Enable w/LO1 command",
                "SD4,SP,10MHz cal,Tamb",
                "SP, 10 MHz cal",
                "Int cal. pot, ext cal. volt",
                "Int cal. pot, ext cal. volt",
                "",
                ""
            ],
            [  # ST5
                "Send PL 1 to enable",
                "Provide stable 1pps inputs",
                "",
                "Provide stable 1pps inputs",
                "Provide accurate 1pps",
                "Provide stable 1pps inputs",
                "Wait, check 1pps inputs",
                "Provide 1pps input"
            ],
            [  # ST6
                "", "", "", "", "", "", "", ""
            ]
        ]

        def __init__(self, values: str):
            "Parse status bytes values returned by ST? command."
            self._values = [f"{c:08b}" for c in map(int, values.split(","))]

        @property
        def values(self) -> list[str]:
            return self._values

        def __getitem__(self, index):
            if isinstance(index, tuple):
                first, second = index
                return self._values[first][second]
            else:
                return self._values[index]

        def to_str(self, indent: int = 0, compress: bool = False):
            """Return the string representation of status bytes.
            
            Parameters
            ==========
            indent: int
                The number of spaces before each line. Default is 0.
            compress: bool
                If `True`, only lines with set bit is printed. Default is `False`.
            
            Returns
            =======
            String representation of status bytes
            """
            width = max(len(each) for block in self.CONDITIONS for each in block)
            out = io.StringIO()
            for i, (bits, name, descriptions, actions) in enumerate(zip(self._values, self.BYTES, self.CONDITIONS, self.CORRECTIVE_ACTIONS)):
                print(f"{'':{indent}s}{bits} {name}", file=out)
                for j, (bit, description, action) in enumerate(zip(bits[::-1], descriptions[::-1], actions[::-1])):
                    if compress:
                        if bit != "1":
                            continue
                        else:
                            bars = ""
                            for k in range(7 - j):
                                if bits[k] == "1":
                                    bars += "│"
                                else:
                                    bars += " "
                    else:
                        bars = "│" * (7 - j)
                    print(" " * indent + bars + "└" +  "─" * j + "─────", f"{description:{width}s}", "  " if action else "", action, file=out)
            return out.getvalue().rstrip()

        def __str__(self) -> str:
            return str(self._values)

        def __repr__(self) -> str:
            return self.to_str()
