__version__ = '0.1.0'

answer = ""
def out(value):
  print(value)
def in(value, save):
  if save:
    answer = input(value)
  else:
    input(value)
def func(name, params, code):
  exec(f"def {name}({params}):\n\t{code}")