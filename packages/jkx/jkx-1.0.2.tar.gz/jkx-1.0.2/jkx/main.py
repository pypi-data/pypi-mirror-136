import sys
import inquirer
import json
import os

os.system('cls' if os.name == 'nt' else 'clear')

f = open(sys.argv[1])
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

  print(gen_path())
  
  if (type(json_data[next_key]) != str):
    explore_json(json_data[next_key])

def gen_path():
  path = "Path = /"
  for node in nodes:
    path += str(node) + '/'
  return path

def start():
  explore_json(data)

if __name__ == "__main__":
   start()
