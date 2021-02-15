
"""
Simple OLED Class mainly for ease of use
"""

import time 

import board
import busio
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import psutil

class OLED:

  def __init__(self, width=128, height=32, i2c=0x3C):
    """
    Args:
      width: OLED screen width
      height: OLED screen height
      i2c: I2C register location
    """
    i2c = board.I2C()
    self.oled = adafruit_ssd1306.SSD1306_I2C(width, height, i2c)

    self.image = Image.new("1", (self.oled.width, self.oled.height))
    self.draw = ImageDraw.Draw(self.image)
    self.font = ImageFont.load_default()
    self._last_screen = None
    self._is_on = True

  def is_on(self):
    return self._is_on

  def clear(self):
    # self.oled.fill(0)
    # self.oled.show()
    self.draw.rectangle((0 ,0, self.oled.width, self.oled.height), outline=0, fill=0)

  def power_on(self):
    self._is_on = True
    self.oled.poweron()
    if self._last_screen is not None:
      self.display(self._last_screen)

  def power_off(self):
    self._is_on = False
    self.oled.poweroff()

  def display(self, disp_text, center_align=True):
    if not isinstance(disp_text, list):
      disp_text = list(disp_text)
    self._last_screen = disp_text
    self.clear()

    for i, t in enumerate(disp_text):
      (font_width, font_height) = self.font.getsize(t)
      if center_align:
        x_pos = self.oled.width/2 - font_width/2
      else:
        x_pos = 0
      y_pos = 0 + i*self.oled.height/len(disp_text) + 1*i
      # print(f'Text: {t}, x_pos: {x_pos}, y_pos: {y_pos}, text width: {self.font.getsize(t)}')
      self.draw.text((x_pos, y_pos), t, font=self.font, fill=255)

    self.oled.image(self.image)
    self.oled.show()


if __name__ == '__main__':
  # Some simple testing
  oled = OLED()
  oled.display(['-------------', 'Starting Up!!!!', '-------------'])

  try:
    while True:
      print(f'Displaying OLED Text!')
      time.sleep(5)
  except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
      print("Keyboard exception occurred")
  except Exception as ex:
      print("ERROR: an unhandled exception occurred: " + str(ex))
  finally:
      GPIO.cleanup()
      print("OLED test terminated")