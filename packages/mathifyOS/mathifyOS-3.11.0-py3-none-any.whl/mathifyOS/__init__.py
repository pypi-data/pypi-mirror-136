import time
import os
import shutil
import math
import random
import sys
console = 'console'
def add(a, b):
  return a + b
def subtract(a, b):
  return a - b
def divide(a, b):
  return a / b
def multiply(a, b):
  return a * b
def more(a, b):
  if a > b:
    return 'True'
  elif a == b:
    return 'Equal'
  else:
    return 'False'
def wait(num):
  time.sleep(num)
def clear(console):
  if console == console:
    command = 'clear'
    if os.name in ('nt', 'dos'):
      command = 'cls'
    os.system(command)
def run(runfile):
  with open(runfile,"r") as rnf:
    exec(rnf.read())
def ren(file, newfile):
  os.rename(file, newfile)
def rem(file):
  os.remove(file)
def infinitysnap(file):
  shutil.rmtree(file)
def pi():
  return math.pi
def area(height, width):
  return height * width
def perimeter(height, width):
  return height + width * 2
def rand(a, b):
  random.randint(a, b)
def no(reason):
  sys.exit(reason)
def haha():
  sys.exit('LOL')