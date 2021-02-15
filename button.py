"""
Class for a simple momentary button
"""

import time
import RPi.GPIO as GPIO


class Button(object):
  """ Detect edges on the given GPIO channel. Skeleton loosely based on Button driver from Google VoiceHat and gpiozero button class """

  def __init__(self, channel, pull_up_down=GPIO.PUD_UP, debounce_time=0.08, on_press=None, on_release=None, on_hold=None, hold_time=1, hold_repeat=False):
    """ 
    Args:
      channel: the GPIO pin number to use (BCM mode)
      pull_up_down: whether the port should be pulled up or down; defaults to GPIO.PUD_UP.
      debounce_time: the time used in debouncing the button in seconds.
      on_press: Callback called when button pressed
      on_release: Callback called when button released
      on_hold: Callback called when button is held according to hold_time and hold_repeat rules
      hold_time: Length of time before calling on_press callback
      hold_repeat: Whether the on_hold callback should be repeated if the button is held down

    TODO: on_release sometimes get called multiple times when releasing button
    """

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.IN, pull_up_down=pull_up_down)
    GPIO.add_event_detect(channel, GPIO.BOTH, callback=self._debounce_and_callback)

    self._channel = int(channel)
    self._pull_up_down = pull_up_down
    self._expected_value = not GPIO.input(self._channel) # Assumes that the button is NOT pressed on startup
    self._debounce_time = debounce_time
    self._hold_time = hold_time
    self._hold_repeat = hold_repeat

    self._next_state = not GPIO.input(self._channel)
    self._last_press_time = None
    self._last_release_time = None
    self._on_press_cb = on_press if on_press else None
    self._on_release_cb = on_release if on_release else None
    self._on_hold_cb = on_hold if on_hold else None

  def __del__(self):
      self.cleanup()

  def wait_for_press(self, timeout=None):
    """ Wait for the button to be pressed or timeout is reached.

    This method blocks until the button is pressed or timeout reached.
    timeout: Number of seconds before releasing block
    """
    # print(f'Waiting for button to be pressed!')
    start = time.time()
    while timeout is None or time.time() - start < timeout:
      if self._last_press_time and self._last_press_time >= start:
        break
      time.sleep(0.02)

  def wait_for_release(self, timeout=None):
    """ Wait for the button to be pressed or timeout is reached.

    This method blocks until the button is pressed or timeout reached.
    timeout: Number of seconds before releasing block
    """
    # print(f'Waiting for button to be released!')
    start = time.time()
    while timeout is None or time.time() - start < timeout:
      if self._last_release_time and self._last_release_time >= start:
        break
      time.sleep(0.02)

  def held_time(self):
    if self.is_pressed() and self._last_press_time:
      return time.time() - self._last_press_time
    else:
      return 0

  def is_held(self):
    return self.held_time() > 0

  def is_pressed(self):
    """ Detect if the button is pressed or not """
    # print(f'is_pressed GPIO input state: {GPIO.input(self._channel)}, expected_value: {self._expected_value}, debounce: {self._debounce()}')
    return bool(self._next_state)

  def on_press(self, callback):
    """ Register on button press callback """
    self._on_press_cb = callback

  def on_release(self, callback):
    """ Register on button release callback """
    self._on_release_cb = callback

  def on_hold(self, callback):
    """ Register on button hold callback - relies on hold_time and hold_repeat options """
    self._on_hold_cb = callback

  def _debounce_and_callback(self, _):
    """ Debounce callbacks """
    if self._debounce():
      self._next_state = not self._next_state
      self._state = GPIO.input(self._channel)

      if GPIO.input(self._channel) == self._expected_value:
        # print('Button pressed!')
        self._last_press_time = time.time()
        if self._on_press_cb:
          self._on_press_cb(self._channel)

        # Handle hold_repeat logic and timing here
        last_hold_time = time.time()
        if self._on_hold_cb is not None:
          while GPIO.input(self._channel) == self._expected_value:
            if time.time() - last_hold_time <= self._hold_time:
              # Only trigger callback once every "_hold_time" seconds
              continue
            last_hold_time = time.time()

            # print(f'Button held for {self.held_time()} seconds (triggered every {self._hold_time} second).')
            self._on_hold_cb(self._channel)
            if not self._hold_repeat:
              break
            time.sleep(0.01)
      
      else:
        # print('Button released!')
        self._last_release_time = time.time()
        if self._on_release_cb:
          self._on_release_cb(self._channel)


  def _debounce(self):
      """ Debounce button press to avoid on <-> off """
      start = time.time()
      while time.time() < start + self._debounce_time:
        if GPIO.input(self._channel) != self._next_state:
          return False
        time.sleep(0.01)
      return True

  def cleanup(self):
    GPIO.cleanup()



if __name__ == '__main__':
  def btn_interrupt(channel):
    print(f'Button on_press interrupt called on channel: {channel}')

  BTN_PIN_GROUNDED = 20
  btn = Button(BTN_PIN_GROUNDED, debounce_time=0.2, on_press=btn_interrupt)

  try:
    while True:
      time.sleep(1)
      print(f'Button is_pressed: {btn.is_pressed()}')
  except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
      print("keyboard exception occurred")
  except Exception as ex:
      print("ERROR: an unhandled exception occurred: " + str(ex))
  finally:
      # GPIO.cleanup()
      print("Button test terminated")
      btn.cleanup()