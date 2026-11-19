import board 
import digitalio
import time
import usb_midi
import adafruit_midi
import rotaryio


from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff


encoderHandler = EncoderHandler()
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

keys_pins = [board.GP6, board.GP7,board.GP8,board.GP9,board.GP10,board.GP11,board.GP12]
buttons_pins = [board.TX, board.RX]


notes = [60, 62, 64, 65, 67, 69, 71]
keys = []
for pin in keys_pins:
    key = digitalio.DigitalInOut(pin)
    key.switch_to_input(pull=digitalio.Pull.UP)
    keys.append(key)

was_pressed = [False] * len(buttons)

encdoer_1 = rotaryio.IncrementalEncoder(
    board.GP1, board.GP2
)  
encoder2 = rotaryio.IncrementalEncoder(
    board.GP3, board.GP4
)

encoders = [encoder1, encoder2]
last_positions = [encoder.position for encoder in encoders]

while True:
    # Buttons: send Note On when pressed, Note Off when released.
    for i, key in enumerate(keys):
        pressed = not key.value  # Pull-up input reads False when pressed

        if pressed and not was_pressed[i]:
            midi.send(NoteOn(notes[i], 100))
        elif was_pressed[i] and not pressed:
            midi.send(NoteOff(notes[i], 0))

        was_pressed[i] = pressed

    # Encoders: turn to change and send their CC values.
    for i, encoder in enumerate(encoders):
        position = encoder.position
        if position != last_positions[i]:
            direction = 1 if position > last_positions[i] else -1
            cc_values[i] = max(0, min(127, cc_values[i] + direction))
            midi.send(ControlChange(cc_numbers[i], cc_values[i]))
            last_positions[i] = position

    time.sleep(0.005)


