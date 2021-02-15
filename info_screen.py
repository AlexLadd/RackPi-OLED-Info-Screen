"""
RackPi Raspberry pi OLED program

Inspired by: https://www.thingiverse.com/thing:3022136

Created: Feb 12, 2021
"""


from button import Button
from rgb_led import RGBLED
from oled import OLED
import RPi.GPIO as GPIO
import time
import subprocess
import psutil
import logging
from logging.handlers import RotatingFileHandler
import traceback 

LOG_FILE = 'rackpi_logs.log'
rfh = RotatingFileHandler(
    filename=LOG_FILE, 
    mode='a',
    maxBytes=5*1024*1024,
    backupCount=2,
    encoding=None,
    delay=0
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(filename)s.%(funcName)2s() - %(lineno)s: %(message)s",
    handlers=[
        # logging.FileHandler(LOG_FILE),
        rfh,
        logging.StreamHandler()
    ]
)

logging.info('Starting up rackpi!!!')

BTN_PIN_GROUNDED = 20
LED_RED = 17
LED_GREEM = 22
LED_BLUE = 27

DISP_TIMEOUT = 5*60
RESET_TO_HOME_SCREEN_TIMEOUT = 60
RESTART_HOLD_TIME = 5
SHUTDOWN_HOLD_TIME = 10

active_screen_num = 0
hold_disp_ticks = 0
is_screen_active = True
needs_update = True
last_action_time = time.time()

# ***   SCREENS   *** 

def intro_screen():
  oled.display(['************', 'Starting Up', '************'])

def info_screen():
  # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
  HOSTNAME =  subprocess.check_output("hostname", shell = True)
  IP = subprocess.check_output("hostname -I | cut -d\' \' -f1", shell = True )
  
  # Examples of getting system information from psutil : https://www.thepythoncode.com/article/get-hardware-system-information-python#CPU_info
  CPU = "{:3.0f}".format(psutil.cpu_percent())
  svmem = psutil.virtual_memory()
  MemUsage = "{:2.0f}".format(svmem.percent)

  cpu_temp = -99
  with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
    cpu_temp = int(float(f.readline().strip()) / 1000)

  text = [
    "NAME: " + HOSTNAME.decode('UTF-8').replace('\n', ''),
    "IP  : " + IP.decode('UTF-8').replace('\n', ''),
    "C:" + CPU.strip() + "% | M:" + MemUsage + "% | T:" + str(cpu_temp) + "°",
    # "CPU: " + CPU.strip() + "% | MEM: " + MemUsage + "% | T: " + str(cpu_temp), # Doesn't fit on the 128x32 screens
  ]

  oled.display(text, center_align=False)

def restart_screen():
  oled.display(['HOLD Button', f'for {RESTART_HOLD_TIME} seconds', 'to RESTART'])

def shutdown_screen():
  oled.display(['HOLD Button', f'for {SHUTDOWN_HOLD_TIME} seconds', 'to SHUTDOWN'])

SCREENS = {
  # -1: {
  #   'name': 'intro_screen',
  #   'screen_func': intro_screen,
  #   'hold_action_time': 0,
  # },
  0: {
    'name': 'info_screen',
    'screen_func': info_screen,
    'hold_action_time': 0,
    'led_colour': 'green'
  },
  1: {
    'name': 'restart_screen',
    'screen_func': restart_screen,
    'hold_action_time': RESTART_HOLD_TIME,
    'led_colour': 'yellow'
  },
  2: {
    'name': 'shutdown_screen',
    'screen_func': shutdown_screen,
    'hold_action_time': SHUTDOWN_HOLD_TIME,
    'led_colour': 'orange'
  },
}

# ***   END SCREENS   *** 


def map_screen_to_name(screen):
  return SCREENS.get(screen, {}).get('name', 'Unkown')

def map_screen_to_func(screen):
  return SCREENS.get(screen, {}).get('screen_func', 'Unkown')

def get_screen_hold_action_time(screen):
  return SCREENS.get(screen, {}).get('hold_action_time', 0)
  
def get_screen_led_colour(screen):
  return SCREENS.get(screen, {}).get('led_colour', 'purple')

def time_since_last_action():
  # logging.info(f'current time: {int(time.time())}, last_action_time: {int(last_action_time)}')
  return int(time.time() - last_action_time)


  # ***   BUTTON FUNCTIONS   *** 

def btn_press(channel):
  # Actions of button press
  global active_screen_num, last_action_time
  # logging.info(f'button pressed, current active_screen_num: {active_screen_num}')
  last_action_time = time.time()


def btn_release(channel):
  # Actions of button release
  global hold_disp_ticks, active_screen_num, last_action_time, needs_update
  # logging.info(f'Button released. hold_disp_ticks: {hold_disp_ticks}, active_screen: {active_screen_num}, oled on: {oled.is_on()}')
  last_action_time = time.time()
  hold_disp_ticks = 0

  # Don't change screen while OLED is off
  if oled.is_on():
    needs_update = True
    active_screen_num += 1
    if active_screen_num > len(SCREENS)-1:
      active_screen_num = 0

  rgb.set_colour(get_screen_led_colour(active_screen_num))


def btn_hold(channel):
  # Actions while button is being held down
  global hold_disp_ticks, active_screen_num, last_action_time
  # logging.info(f'Button held down, current ticks: {hold_disp_ticks}')
  last_action_time = time.time()
  hold_disp_ticks += 1

  if map_screen_to_name(active_screen_num) == 'shutdown_screen' and hold_disp_ticks > get_screen_hold_action_time(active_screen_num):
    logging.info(f'Shutdown hold time reached')
    oled.display(['Shutting down', 'Raspberry Pi', 'Now'])
    subprocess.Popen('sudo shutdown now', shell=True)
    time.sleep(1) # wait so the shutdown screen stays while processing cmd

  elif map_screen_to_name(active_screen_num) == 'restart_screen' and hold_disp_ticks > get_screen_hold_action_time(active_screen_num):
    logging.info(f'Restart hold time reached')
    oled.display(['Restarting', 'Raspberry Pi', 'Now'])
    subprocess.Popen('sudo reboot now', shell=True)
    time.sleep(1) # wait so the shutdown screen stays while processing cmd

  # ***   END BUTTON FUNCTIONS   *** 


rgb = RGBLED(LED_RED, LED_GREEM, LED_BLUE)
rgb.set_colour('green')
oled = OLED()
btn = Button(BTN_PIN_GROUNDED, debounce_time=0.2, on_press=btn_press, on_hold=btn_hold, on_release=btn_release, hold_repeat=True)

def main():
  global needs_update, active_screen_num

  try:
    while True:
      try:
        # Constantly check for screen update
        if needs_update:
          map_screen_to_func(active_screen_num)()
          needs_update = False
      except TypeError as e:
        logging.info(f'Trying to set unknown screen using {active_screen_num}: {traceback.format_exc()}')

      # Check OLED state (ON/OFF) & reset to intro screen after idle and power down after idle for even longer
      if oled.is_on() and time_since_last_action() >= DISP_TIMEOUT:
        # Turn off screen power after being idle for set amount of time
        logging.info(f'Turning screen off since no action has in {DISP_TIMEOUT} seconds ({time_since_last_action()}).')
        oled.power_off()
      elif not oled.is_on() and time_since_last_action() <= DISP_TIMEOUT:
        # Turn on screen power if button push detected
        logging.info('Turning screen on after a recent action.')
        oled.power_on()
      elif oled.is_on() and active_screen_num != 0 and time_since_last_action() >= RESET_TO_HOME_SCREEN_TIMEOUT:
        # Set to info screen after being idle for a period of time 
        # Make sure we are not already on info screen or we will never turn off screen after timeout
        active_screen_num = 0 # Start back at info screen after being inactive for a while
        logging.info(f'Reseting screen to default after being inactive for {time_since_last_action()} seconds.')
        needs_update = True
        last_action_time = time.time()
        rgb.set_colour(get_screen_led_colour(active_screen_num))

      time.sleep(1)

  except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    logging.info("keyboard exception occurred")
  except Exception as ex:
    logging.info(traceback.format_exc())
  finally:
    GPIO.cleanup()
    logging.info("info_screen terminated, check for errors!")
    rgb.set_colour('red')
    oled.display(['Program Exited', '------------', 'Check for Error!'])
    # time.sleep(2)


if __name__ == '__main__':
  main()

