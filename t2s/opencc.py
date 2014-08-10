
import os

def convert(text, config='t2s'):
  text = text.encode('utf-8')
  f = os.popen('t2s --config '+config+' \''+text+'\'')
  return f.read().decode('utf-8')
