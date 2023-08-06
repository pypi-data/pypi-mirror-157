# https://towardsdatascience.com/how-to-upload-your-python-package-to-pypi-de1b363a1b3
__version__ = '0.1.12'
import os, time, sys, random as numbergen
def boolean(txt):
  if txt.lower() == "true":
    return True
  return False
bool = boolean
class FileFunctionError(Exception):
  pass
class ArgumentError(Exception):
  pass
def file(name, function, usage=""):
  try:
    if function.lower() not in ["r", "read", "w", "write", "c", "create", "a", "append", "d", "delete"] or (function.lower() not in ["w", "write", "a", "append"] and usage != "") or (function.lower() in ["w", "write", "a", "apppend"] and usage == ""):
      raise FileFunctionError
    if function.lower() in ["r", "read"]:
      return open(name, "r").read()
    elif function.lower() in ["w", "write"]:
      open(name, "w").write(usage)
    elif function.lower() in ["a", "append"]:
      open(name, "a").write(usage)
    elif function.lower() in ["c", "create"]:
      open(name, "w").write("")
    elif function.lower() in ["d", "delete"]:
      os.remove(name)
  except:
    raise FileFunctionError
def read(txt):
  return file(txt, "r")
def create(txt):
  file(txt, "c")
def write(txt, txt2):
  file(txt, "w", txt2)
def append(txt, txt2):
  file(txt, "a", txt2)
read_file = read
write_file = write
append_file = append
create_file = create
def delete_file(txt):
  file(txt, "d")
def print_delay(txt, num=0.2):
  for x in txt:
    sys.stdout.write(x)
    sys.stdout.flush()
    time.sleep(num)
  sys.stdout.write("\n")
def sleep(num=1):
  time.sleep(num)
pause = sleep
def if_function(var, f1, f1v, f2="", f2v=""):
  if var:
    array_function(f1, f1v)
  elif f2v != "":
    array_function(f2, f2v)
if_func = if_function
if_func_else = if_function
if_function_else = if_function
def if_print(var, txt1, txt2=""):
  if_function(var, print, [txt1], print, [txt2])
if_print_else = if_print
def randint(num1="", num2=""):
  if num2 == "":
    if num1 == "":
      num1 = 0
      num2 = 10
    else:
      num2 = num1
      num1 = 0
  return numbergen.randint(num1, num2)
def random(num1="", num2=""):
  if num2 == "":
    if num1 == "":
      num1 = 0
      num2 = 1
    else:
      num2 = num1
      num1 = 0
  if num1 > num2:
    raise ArgumentError
  value = numbergen.random() + num1
  value = value * num2
  if value > num2:
    value = num2
  return value
def switch(var, id="global"):
  globals()[f"StythonSwitchValue{id}"] = var
def case(value, id="global"):
  if globals()[f"StythonSwitchValue{id}"] == value:
    return True
  return False
def end_switch(id="global"):
  del globals()[f"StythonSwitchValue{id}"]
def fibonacci(n):
  sequence = []
  a, b = 0, 1
  while b < n:
    sequence.append(b)
    a, b = b, a + b
  return sequence
fib = fibonacci
def array_function(function, parameters):
  function(*parameters)
array_parameters = array_function
array_param = array_function
array_func = array_function
class HexError(Exception):
  pass
def hex(num, function="hex", num2=""):
  if function.lower() not in ["a", "add", "s", "subtract", "m", "multiply", "d", "div", "divide", "dec", "decimal", "h", "hex", "simple", "simplehex"]:
    raise HexError
  decnum = int(f"{num}", 16)
  if function.lower() in ["simple", "simplehex"]:
    if num != int(num):
      raise HexError
    hex = "0"
    for x in range(0, num):
      if hex[len(hex) - 1] in ["0", "1", "2", "3", "4", "5", "6", "7", "8"]:
        newx = str(int(x) + 1)
      elif hex[len(hex) - 1].lower() == "9":
        newx = "a"
      elif hex[len(hex) - 1].lower() == "a":
        newx = "b"
      elif hex[len(hex) - 1].lower() == "b":
        newx = "c"
      elif hex[len(hex) - 1].lower() == "c":
        newx = "d"
      elif hex[len(hex) - 1].lower() == "d":
        newx = "e"
      elif hex[len(hex) - 1].lower() == "e":
        newx = "f"
      elif hex[len(hex) - 1].lower() == "f":
        raise HexError
      newhex = ""
      loopNum = 0
      for x in hex:
        loopNum = loopNum + 1
        if loopNum == len(hex):
          newhex = newhex + newx
        else:
          newhex = newhex + x
      hex = newhex
    return hex.upper()