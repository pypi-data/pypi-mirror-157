import os,sys,yaml
from .constants import *

def load_yaml(name, folder=PIPE_FOLDER):
    filename = f'{name}.yml'
    path = os.path.join(folder, filename)
    with open(path, 'r') as file:
        yml = yaml.safe_load(file)
        return yml

def load_yamls(folder=PIPE_FOLDER):
    ydict = {}
    for root, dirs, files in os.walk(folder):
       print(f'load_yamls: {root}')
       for name in files:
          split = name.split('.')
          key = split[0]
          if 'yml' in split: ydict[key] = load_yaml(key, root)
    return ydict

def load_module(module_name):
    mod = __import__(module_name, globals=None, locals=None, fromlist=False)
    return mod
