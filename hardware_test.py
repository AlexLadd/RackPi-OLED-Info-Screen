"""
Quick Hardware Test
"""

from button import Button
from rgb_led import RGBLED
from oled import OLED

BTN_PIN_GROUNDED = 20
LED_RED = 17
LED_GREEM = 22
LED_BLUE = 27


def btn_press(channel):
  print('button pressed')
def btn_hold(channel):
  print('button held')
def btn_release(channel):
  print('button released')


oled = OLED()
rgb = RGBLED(LED_RED, LED_GREEM, LED_BLUE)
btn = Button(BTN_PIN_GROUNDED, debounce_time=0.2, on_press=btn_press, on_hold=btn_hold, on_release=btn_release, hold_repeat=True)

print('Waiting for button press. Testing button press.')
oled.display(['TESTING', 'Press Button', 'TESTING'])
btn.wait_for_release()

print('Waiting for button hold. Testing button hold.')
oled.display(['TESTING', 'Hold Button', 'TESTING'])
btn.wait_for_release()

print('Testing LED - ON.')
oled.display(['TESTING', 'LED ON', 'TESTING'])
rgb.set_colour('red')
btn.wait_for_release(5)

print('Testing LED - OFF.')
oled.display(['TESTING', 'LED OFF', 'TESTING'])
rgb.off()
btn.wait_for_release(5)

print('Quick test complete!')
oled.display(['TESTING', 'TEST DONE!', 'TESTING'])




