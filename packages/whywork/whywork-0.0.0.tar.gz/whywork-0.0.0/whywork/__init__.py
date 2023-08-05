import time, socket, os, math
from datetime import datetime
def ctime():
  now = datetime.now()
  current_time = now.strftime("%H:%M:%S")
  return f'Current Time Is: {current_time}.'
def xtime():
  now = datetime.now()
  current_time = now.strftime("%H:%M:%S")
  return f'{current_time}'
def wait(numOfSeconds):
  return time.wait(numOfSeconds)
def cmd(commandName):
  return os.system(commandName)
def filemake(fileName, extension):
  return cmd(f'touch {fileName}.{extension}')
def ip():
  hostname = socket.gethostname()
  ip_addr = socket.gethostbyname(hostname)
  return ip_addr
def libs():
  return cmd('pip3 freeze >> requirements.txt')
def power(Number, Power):
  return Number ** Power
def pipget(PackageName):
  return cmd(f'pip3 install {PackageName}')
def mfact(Number):
  return math.factorial(Number)
def numvalue(Num1, Num2):
  if Num1 > Num2:
    return Num1
  elif Num1<Num2:
    return Num2
  elif Num1 == Num2:
    return 'equal'