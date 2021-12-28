from simple_language import *

class Interpreter(object):
    def __init__(self, pc, stack, code):
        self.pc = pc
        self.stack = stack
        self.code = code

    def at_each_step(self):
        pass

    def run_PUSH(self):
        #print("Running PUSH")
        self.stack.append(self.code[self.pc+1])
        self.pc += 2

    def run_GT(self):
        #print("Running GT")
        if self.stack[-1] > self.code[self.pc+1]:
            self.pc = self.code[self.pc+2]
        else:
            self.pc += 3

    def run_ADD(self):
        #print("Running ADD")
        self.stack[-1] += self.code[self.pc+1]
        self.pc += 2

    def run_JUMP(self):
        #print("Running JUMP")
        self.pc = self.code[self.pc+1]

    def run_POP(self):
        #print("Running POP")
        self.stack.pop()
        self.pc += 1

    def interpret(self):
        while True:
            print("running ", self.pc)
            instruction_to_run = self.code[self.pc]
            self.at_each_step()

            if instruction_to_run == PUSH:
                self.run_PUSH()
            elif instruction_to_run == GT:
                self.run_GT()
            elif instruction_to_run == ADD:
                self.run_ADD()
            elif instruction_to_run == JUMP:
                self.run_JUMP()
            elif instruction_to_run == POP:
                self.run_POP()
            elif instruction_to_run == HALT:
                #print("HALT")
                return self.stack[-1]

def interpret(code):
    return Interpreter(0, [], code).interpret()
