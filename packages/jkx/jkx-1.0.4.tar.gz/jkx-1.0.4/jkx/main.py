import sys
import inquirer
import json
import os
import argparse

os.system('cls' if os.name == 'nt' else 'clear')

parser = argparse.ArgumentParser(
  prog='jkx', 
  description='Select which JSON file to explore',
  epilog='Example: jkx openapi.json'
)
parser.add_argument('-f', action="store", dest="file")
parser.add_argument(
  '-js', action="store_true", dest="javascript",
  help='Print path in JavaScript notation'
)
parser.add_argument(
  '-py', action="store_true", dest="python",
  help='Print path in Python notation'
)
args = parser.parse_args()

f = open(args.file)
data = json.load(f)

nodes = []

def gen_array_keys(array):
  index_array = []
  for i in range(len(array)):
    index_array.append(i)
  
  return index_array

def explore_json(json_data):
  keys = []
  if (type(json_data) == list):
    keys = gen_array_keys(json_data)
  else:
    for key, value in json_data.items():
      keys.append(key + ' (' + str(type(value)).split("'")[1] + ')')

  questions = [
      inquirer.List('key',
        message="Select a key from the JSON data",
        choices=keys,
      ),
    ]

  answer = inquirer.prompt(questions)
  if (type(answer['key']) == str):
    next_key = answer['key'].split(' ')[0]
  else:
    next_key = answer['key']

  nodes.append(next_key)

# Handle flags
  if (args.javascript):
      print(gen_js_path())
  elif (args.python):
      print(gen_py_path());
  else:
      print(gen_path());
  
  if (type(json_data[next_key]) != str):
    explore_json(json_data[next_key])

def gen_path():
  path = "Path = /"
  for node in nodes:
    path += str(node) + '/'
  return path

def gen_js_path():
  js_path = 'Path = data'
  for node in nodes:
    if (type(node) == int):
      js_path += '[' + str(node) + ']'
    else:
      js_path += '.' + str(node)
  return js_path

def gen_py_path():
  py_path = 'Path = data'
  for node in nodes:
    if (type(node) == int):
      py_path += '[' + str(node) + ']'
    else:
      py_path += '[\'' + str(node) + '\']'
  return py_path

def start():
  explore_json(data)

if __name__ == "__main__":
   start()