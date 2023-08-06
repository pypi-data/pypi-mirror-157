from .constants import *
from .schema import Schema

class Pipe:
    def __init__(self, reg, yml):
        self.registry = reg
        self.source = yml
        self.assembly = []
        self.next_index = 0
        self.vars = {K_VAR: FIRST_ID}

    def substitute(self, action):
        for key, value in action.items():
            if isinstance(value, str) and value[0] == K_VAR:
                var = value[1:]
                action[key] = self.vars[var]
        return action

    def init(self, action):
        self.registry.load(action['imports'])
        if action['set']:
            for k,v in action['set'].items(): self.vars[k] = v
        return self

    def compile(self):
        for id, action in self.source.items():
            action['id'] = id
            if action['do'] == K_INIT:
                self.init(action)
            else:
                self.substitute(action)
                asm = self.registry.assemble(action)
                self.assembly.append(asm)
            self.vars[K_VAR] = id
        return self.assembly

    def run(self):
        vm = {}
        if len(self.assembly) == 0: self.compile()
        for da in self.assembly:
            method = da.CODE
            frame = method(vm, da)
            vm.setdefault(da.id, frame)
        return vm
