"""
Class to control an RGB LED via PWM

Inspired by: https://github.com/bobataylor/RPy-LED-Controller/blob/master/leds.py
"""

import time
import RPi.GPIO as GPIO


GAMMA = [\
0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,\
0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,\
1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,\
2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,\
5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,\
10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,\
17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,\
25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,\
37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,\
51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,\
69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,\
90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,\
115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,\
144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,\
177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,\
215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255]

red           = [255, 0,   0]
orange        = [255, 128, 0]
yellow        = [255, 200, 0]
green         = [0,   255, 0]
blue          = [0,   0,   255]
purple        = [127, 0,   255]
pink          = [155, 0,   127]
white         = [255, 255, 255]
dark_orange   = [153, 76, 0]

COLOUR_MAP = {"red":red, "orange":orange, "yellow":yellow, "green":green, "blue":blue, "purple":purple, "white":white, "dark":dark_orange, "pink":pink}



class Channel:
  """
  Class that represents a single colour of a RGB LED
  """

  def __init__(self, pin, freq, duty):
    self.pin = pin
    self.frequency = freq
    self.duty_cycle = duty
    self.pwm = None

  def set_duty(self, duty):
    self.duty_cycle = duty
    self.pwm.ChangeDutyCycle(int(duty))

  def on(self):
    GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
    self.pwm = GPIO.PWM(self.pin, self.frequency)
    self.pwm.start(self.duty_cycle)

  def off(self, duty):
    self.duty_cycle = 0
    self.set_duty(0)


class RGBLED(object):
  """ Simple RGB PWM LED Driver inspired by: https://github.com/bobataylor/RPy-LED-Controller/blob/master/leds.py """

  def __init__(self, red, green, blue, freq=100, initial_colour=(0,0,0)):
    """
    Args:
      red: Red LED Pin
      green: green LED Pin
      blue: blue LED Pin
      freq: PWM frequency
      initial_colour: Colour RGB LED will turn on to when setup
    """
    GPIO.setmode(GPIO.BCM)

    self.red_pin, self.green_pin, self.blue_pin = red, green, blue
    self.frequency = freq
    self.currenct_colour = initial_colour

    GPIO.setmode(GPIO.BCM) 
    self.red = Channel(red, freq, 0)
    self.green = Channel(green, freq, 0)
    self.blue = Channel(blue, freq, 0)
    self.channels = [self.red, self.green, self.blue]

    self.on()
    self.set_colour(initial_colour)

  def __del__(self):
      self.cleanup()

  def cleanup(self):
    GPIO.cleanup()

  def on(self):
    for c in self.channels:
      c.on()

  def off(self):
    for c in self.channels:
      c.off()

  def set_colour(self, colour):
    """
    Changes the color of the leds.
    Custom colors can be set by providing color as an array of r b g values.
    Any color is the combination of the R G B channels at varying intensities. The different intensities are achieved by varying the on/off ratio of the lights, also known as the duty cycle. Duty cycles can be between 0 (always ofF) to 100 (always on).
    We determine duty cycle by taking the ratio of the given value for the channel to its max value (value/256) then multiplying by 100.
    """
    if not isinstance(colour, list):
      if colour in COLOUR_MAP:
        colour = COLOUR_MAP[colour]
      else:
        if isinstance(colour, tuple):
          colour = list(colour)
        else:
          raise TypeError(f'Invalid colour: {colour}')
    colour = [int(x) for x in colour]
    self.currenct_colour = colour

    for i in range(0, 3):
      if colour[i] < 0: colour[i] = 0
      if colour[i] > 255: colour[i] = 255

      duty_cycle = (float(GAMMA[colour[i]])/255.0) * 100.0
      self.channels[i].set_duty(duty_cycle)


if __name__ == '__main__':
  LED_RED = 17
  LED_GREEM = 22
  LED_BLUE = 27
  rgb = RGBLED(LED_RED, LED_GREEM, LED_BLUE)
  rgb.set_colour('green')

  try:
    x, y, z = 0, 0, 0
    while True:
      z = z + 1 if z < 255 else 0
      for y in range(1,255):
        c = (z, x, y)
        rgb.set_colour(c)
        time.sleep(0.01)
        for x in range(1,255):
          c = (z, x, y)
          rgb.set_colour(c)
          time.sleep(0.01)
  except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
      print("keyboard exception occurred")
  except Exception as ex:
      print("ERROR: an unhandled exception occurred: " + str(ex))
  finally:
      GPIO.cleanup()
      print("RGB test terminated")
