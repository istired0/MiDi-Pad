import board 
import digitalio
import time
import usb_midi
import adafruit_midi
import rotaryio
import analogio
import neopixel

from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange


pixels = neopixel.NeoPixel(
    board.GP13,
    6,                 #n_of_LEDs
    brightness=0.3,
    auto_write=True,
)

def color_wheel(pos):
    pos = pos % 256
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

keys_pins = [board.GP6, board.GP7,board.GP8,board.GP9,board.GP10,board.GP11,board.GP12]
buttons_pins = [board.TX, board.RX]



encoder1 = rotaryio.IncrementalEncoder(
    board.GP1, board.GP2
)  
encoder2 = rotaryio.IncrementalEncoder(
    board.GP3, board.GP4
)

slider = analogio.AnalogIn(board.GP5)  

notes = [60, 62, 64, 65, 67, 69, 71]
keys = []
encoders = [encoder1, encoder2]


for pin in keys_pins:
    key = digitalio.DigitalInOut(pin)
    key.switch_to_input(pull=digitalio.Pull.UP)
    keys.append(key)

was_pressed = [False] * len(keys)


cc_numbers = [1, 2]
cc_values = [64, 64]
last_positions = [encoder.position for encoder in encoders]

last_slider_cc = -1


while True:
    slider_cc = slider.value * 127 // 65535

    if slider_cc != last_slider_cc:
        midi.send(ControlChange(10, slider_cc))  
        last_slider_cc = slider_cc

    for i, key in enumerate(keys):
        pressed = not key.value 

        if pressed and not was_pressed[i]:
            midi.send(NoteOn(notes[i], 100))
        elif was_pressed[i] and not pressed:
            midi.send(NoteOff(notes[i], 0))

        was_pressed[i] = pressed

    for i, encoder in enumerate(encoders):
        position = encoder.position
        if position != last_positions[i]:
            direction = 1 if position > last_positions[i] else -1
            cc_values[i] = max(0, min(127, cc_values[i] + direction))
            midi.send(ControlChange(cc_numbers[i], cc_values[i]))
            last_positions[i] = position
    # Continuously animate the LEDs
    offset = int(time.monotonic() * 30)

    for i in range(len(pixels)):
        pixels[i] = color_wheel(offset + i * 256 // len(pixels))

    time.sleep(0.005)


