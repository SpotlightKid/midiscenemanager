# -*- coding: utf-8 -*-
#
# midiio.py
#
"""Wrapper clas for rtmidi.MidiOut to facilitate sending common MIDI events."""

import binascii

import rtmidi
from rtmidi.midiconstants import *
from rtmidi.midiutil import open_midioutput

from .sequencer import SequencerThread


def parse_sysex_string(s):
    return binascii.unhexlify(s.replace(' ', ''))


class MidiOutWrapper:
    def __init__(self, midi, name, ch=1):
        self.channel = ch
        self.midi = midi
        self.name = name

    @property
    def midi(self):
        return self._midi

    @midi.setter
    def midi(self, obj):
        if hasattr(self, '_midi'):
            with self._midi.lock:
                self._midi.midiout = obj
        else:
            self._midi = SequencerThread(obj)
            self._midi.start()

    def _cleanup(self):
        self.midi.stop()
        self.midi.midiout.close_port()

    def send_channel_message(self, status, data1=None, data2=None, ch=None, delay=0):
        """Send a MIDI channel mode message."""
        msg = [(status & 0xf0) | ((ch if ch else self.channel) - 1 & 0xF)]
        if data1 is not None:
            msg.append(data1 & 0x7F)
            if data2 is not None:
                msg.append(data2 & 0x7F)
        self.midi.add(msg, delta=delay)

    def send_system_common_message(self, status=0xF7, data1=None, data2=None):
        msg = [status & 0xF7]
        if msg[0] in (0xF1, 0xF2, 0xF3):
            msg.append(data1 & 0x7F)
        if msg[0] == 0xF2:
            msg.append(data2 & 0x7F)
        self.midi.add(msg, delta=delay)

    def send_system_realtime_message(self, status=0xF8):
        self.midi.add([status & 0xF7], delta=1)

    def send_system_exclusive(self, value=""):
        msg = parse_sysex_string(value)
        if (msg and msg.startswith(b'\xF0') and msg.endswith(b'\xF7') and
                all((val < 128 for val in msg[1:-1]))):
            self.midi.add(msg, delta=delay)
        else:
            raise ValueError("Invalid sysex string: %s", msg)

    def send_note_off(self, note=60, velocity=0, ch=None, delay=0):
        """Send a 'Note Off' message."""
        self.send_channel_message(NOTE_OFF, note, velocity, ch=ch, delay=delay)

    def send_note_on(self, note=60, velocity=127, ch=None, delay=0):
        """Send a 'Note On' message."""
        self.send_channel_message(NOTE_ON, note, velocity, ch=ch, delay=delay)

    def send_poly_pressure(self, note=60, value=0, ch=None, delay=0):
        """Send a 'Polyphonic Pressure' (Aftertouch) message."""
        self.send_channel_message(POLY_PRESSURE, note, value, ch=ch, delay=delay)

    def send_control_change(self, cc=0, value=0, ch=None, delay=0):
        """Send a 'Control Change' message."""
        self.send_channel_message(CONTROL_CHANGE, cc, value, ch=ch, delay=delay)

    def send_program_change(self, program=0, ch=None, delay=0):
        """Send a 'Program Change' message."""
        self.send_channel_message(PROGRAM_CHANGE, program, ch=ch, delay=delay)

    def send_channel_pressure(self, value=0, ch=None, delay=0):
        """Send a 'Polyphonic Pressure' (Aftertouch) message."""
        self.send_channel_message(CHANNEL_PRESSURE, value, ch=ch, delay=delay)

    def send_pitch_bend(self, value=8192, ch=None, delay=0):
        """Send a 'Program Change' message."""
        self.send_channel_message(PITCH_BEND, value & 0x7f, (value >> 7) & 0x7f, ch=ch,
                                  delay=delay)

    def send_bank_select(self, bank=None, msb=None, lsb=None, ch=None, delay=0):
        """Send 'Bank Select' MSB and/or LSB 'Control Change' messages."""
        if bank is not None:
            msb = (bank << 7) & 0x7F
            lsb = bank & 0x7F

        if msb is not None:
            self.send_control_change(BANK_SELECT_MSB, msb, ch=ch, delay=delay)

        if lsb is not None:
            self.send_control_change(BANK_SELECT_LSB, lsb, ch=ch, delay=delay)

    def send_modulation(self, value=0, ch=None, delay=0):
        """Send a 'Modulation' (CC #1) 'Control Change' message."""
        self.send_control_change(MODULATION, value, ch=ch, delay=delay)

    def send_breath_controller(self, value=0, ch=None, delay=0):
        """Send a 'Breath Controller' (CC #3) 'Control Change' message."""
        self.send_control_change(BREATH_CONTROLLER, value, ch=ch, delay=delay)

    def send_foot_controller(self, value=0, ch=None, delay=0):
        """Send a 'Foot Controller' (CC #4) 'Control Change' message."""
        self.send_control_change(FOOT_CONTROLLER, value, ch=ch, delay=delay)

    def send_channel_volume(self, value=127, ch=None, delay=0):
        """Send a 'Volume' (CC #7) 'Control Change' message."""
        self.send_control_change(CHANNEL_VOLUME, value, ch=ch, delay=delay)

    def send_balance(self, value=63, ch=None, delay=0):
        """Send a 'Balance' (CC #8) 'Control Change' message."""
        self.send_control_change(BALANCE, value, ch=ch, delay=delay)

    def send_pan(self, value=63, ch=None, delay=0):
        """Send a 'Pan' (CC #10) 'Control Change' message."""
        self.send_control_change(PAN, value, ch=ch, delay=delay)

    def send_expression(self, value=127, ch=None, delay=0):
        """Send a 'Expression' (CC #11) 'Control Change' message."""
        self.send_control_change(EXPRESSION_CONTROLLER, value, ch=ch, delay=delay)

    def send_all_sound_off(self, ch=None, delay=0):
        """Send a 'All Sound Off' (CC #120) 'Control Change' message."""
        self.send_control_change(ALL_SOUND_OFF, 0, ch=ch, delay=delay)

    def send_reset_all_controllers(self, ch=None, delay=0):
        """Send a 'All Sound Off' (CC #121) 'Control Change' message."""
        self.send_control_change(RESET_ALL_CONTROLLERS, 0, ch=ch, delay=delay)

    def send_local_control(self, value=1, ch=None, delay=0):
        """Send a 'Local Control On/Off' (CC #122) 'Control Change' message."""
        self.send_control_change(EXPRESSION_CONTROLLER, 0, ch=ch, delay=delay)

    def send_all_notes_off(self, ch=None, delay=0):
        """Send a 'All Notes Off' (CC #123) 'Control Change' message."""
        self.send_control_change(ALL_NOTES_OFF, 0, ch=ch, delay=delay)

    # add more convenience methods for other common MIDI events here...


def get_midiout(port, api="UNSPECIFIED"):
    api = getattr(rtmidi, 'API_' + api)
    midiout, name = open_midioutput(port, api=api, interactive=False, use_virtual=False)
    return MidiOutWrapper(midiout, name)


def get_midiout_ports(api="UNSPECIFIED"):
    mo = rtmidi.MidiOut(rtapi=getattr(rtmidi, 'API_' + api))
    return sorted(mo.get_ports())
