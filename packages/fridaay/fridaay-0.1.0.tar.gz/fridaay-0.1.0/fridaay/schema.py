from collections import namedtuple
import json
from .constants import *

class Schema:
    def __init__(self, act, dad):
        self.act = act
        self.dad = {}
        self.optional = ['doc','save',K_CODE]
        self.keys = ['id','do'] + self.optional
        self.sanitize(dad)
        self.struct = namedtuple(self.act, self.keys)
        self.struct.__doc__ = json.dumps(dad)

    def sanitize(self, dad):
        for k, v in dad.items():
            key = k if k != K_FROM else K_FKEY
            self.dad[key] = v
            self.keys.append(key)
            if v[-1] != '*': self.optional.append(key)

    def default(self, action):
        for k in self.optional:
            if k not in action: action[k] = False
        return action

    def parse(self, action):
        if K_FROM in action: action[K_FKEY] = action.pop(K_FROM)
        defaulted = self.default(action)
        tuple = self.struct(**defaulted)
        return tuple
