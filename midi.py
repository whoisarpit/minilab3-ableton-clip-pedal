import time
import rtmidi
import logging
import argparse
import sys


CONTROL_CHANNEL = 176
NOTE_CHANNEL = 153
MAIN_KNOB_THRESHOLD = 64


class LoopbackAndModify:
    def __init__(
        self,
        input_name: str,
        output_name: str,
        logger: logging.Logger,
        main_knob: int,
        pedal: int,
        min_track: int,
        max_track: int,
        min_track_note: int,
        intercept: bool = False,
    ):
        self.logger = logger
        self.main_knob = [CONTROL_CHANNEL, main_knob]
        self.pedal = [CONTROL_CHANNEL, pedal]
        self.min_track = min_track
        self.track = min_track
        self.max_track = max_track
        self.min_track_note = min_track_note
        self.intercept = intercept
        self.midiin = rtmidi.MidiIn()
        self.midiin.ignore_types(False, False, False)
        self.midiout = rtmidi.MidiOut()
        self.port_in, in_name = self.get_port(self.midiin, input_name)
        self.port_out, out_name = self.get_port(self.midiout, output_name)
        self.logger.debug(f"Input port: {self.port_in} ({in_name})")
        self.logger.debug(f"Output port: {self.port_out} ({out_name})")

    def __enter__(self):
        self.midiin.open_port(self.port_in)
        self.midiout.open_port(self.port_out)
        self.logger.debug("Ports opened")
        self.midiin.set_callback(self)
        self.logger.debug("Callback attached")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.midiin.close_port()
        self.midiout.close_port()
        del self.midiin
        del self.midiout
        self.logger.debug("Ports closed")

    def __call__(self, event, data=None):
        message, deltatime = event
        self.logger.debug(f"Message Received: {message}")
        message = self.intercept_message(message)
        self.midiout.send_message(message)

    def intercept_message(self, message):
        try:
            if not self.intercept:
                return message

            channel, note, velocity, *_extras = message

            if [channel, note] == self.main_knob:
                up = velocity > MAIN_KNOB_THRESHOLD
                self.shift_track(up)

            if [channel, note] == self.pedal:
                if velocity > 0:
                    self.logger.info(f"Activating track {self.track}")
                note = self.min_track_note + (self.track - self.min_track)
                message = [NOTE_CHANNEL, note, velocity]

            return message
        except Exception as e:
            self.logger.error(f"Error in intercept: {e}")
            return message

    def send_message(self, message):
        self.midiout.send_message(message)

    def shift_track(self, up: bool):
        self.track = (
            min(self.max_track, self.track + 1)
            if up
            else max(self.min_track, self.track - 1)
        )
        self.logger.info(f"Selected Track {self.track}")

    def get_port(self, midi, name: str):
        for i, port in enumerate(midi.get_ports()):
            if name in port:
                return i, port
        return None


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Loopback and Modify MIDI messages")
    parser.add_argument("-l", "--log", help="Set log level", type=str, default="INFO")
    parser.add_argument(
        "-s", "--source", help="Set source port name", type=str, default="Minilab3 MIDI"
    )
    parser.add_argument(
        "-b",
        "--loopback",
        help="Set loopback port name",
        type=str,
        default="Arturia Loopback",
    )
    parser.add_argument(
        "--min-track",
        help="Set the minimum track number",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--max-track",
        help="Set the maximum track number",
        type=int,
        default=8,
    )
    parser.add_argument(
        "--min-track-note",
        help="Set the note number for the minimum track",
        type=int,
        default=36,
    )
    parser.add_argument(
        "--main-knob",
        help="Set the main knob control number",
        type=int,
        default=29,
    )
    parser.add_argument(
        "--pedal",
        help="Set the pedal control number",
        type=int,
        default=127,
    )

    args = parser.parse_args(args)

    log_level = getattr(logging, args.log.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level: {args.log}")

    logging.basicConfig(level=log_level)
    in_log = logging.getLogger("MIDI In")
    out_log = logging.getLogger("MIDI Out")

    print("Entering main loop. Press Control-C to exit.")

    kwargs = {
        "main_knob": args.main_knob,
        "pedal": args.pedal,
        "min_track": args.min_track,
        "max_track": args.max_track,
        "min_track_note": args.min_track_note,
    }

    with LoopbackAndModify(
        args.source, args.loopback, in_log, intercept=True, **kwargs
    ) as _loop_in, LoopbackAndModify(
        args.loopback, args.source, out_log, **kwargs
    ) as _loop_out:
        try:
            # Just wait for keyboard interrupt,
            # everything else is handled via the input callback.
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Exiting.")

    # Rest of your code here


if __name__ == "__main__":
    main()
