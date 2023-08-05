from pathlib import Path

from genki_wave.callbacks import ButtonAndDataPrint, CsvOutput
from genki_wave.threading_runner import WaveListener


def main():
    ble_address = "E0:D4:D7:8E:8C:07"
    callbacks = [ButtonAndDataPrint(5), CsvOutput(Path("output.csv"))]
    with WaveListener(ble_address, callbacks) as wave:
        while not wave.comm.cancel:
            pass


if __name__ == "__main__":
    main()
