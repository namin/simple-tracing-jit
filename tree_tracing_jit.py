from simple_language import *
from simple_interpreter import Interpreter

class UnknownTraceRecordError(Exception):
    pass

class TracingInterpreter(Interpreter):
    def __init__(self, pc, stack, code, loops, recording_trace):
        self.loops = loops
        self.recording_trace = recording_trace
        self.jitted_code_scope = {'GuardFailed': GuardFailed, 'self': self}
        self.trace_id = 0

        Interpreter.__init__(self, pc, stack, code)

    def translate_trace(self, loop_info):
        trace = loop_info['trace']
        # create python code to run the trace
        ec = '''
def trace_{id}():
    count = 0
    while True:
        count += 1
        #print('in trace_{id}, iteration '+str(count))
'''.format_map({'id': loop_info['trace_id']})
        def inner(trace, s='', p=[]):
            ec = ''
            if trace is None:
                ec += '''
        {s}raise GuardFailed(count, {p})'''.format_map({'s':s,'p':p})
                return ec
            for (i, trace_step) in enumerate(trace):
                if trace_step[0] == TRACE_INSTR:
                    if trace_step[1] == JUMP:
                        ec += '''
        {s}self.pc = {x}'''.format_map({'s':s,'x':trace_step[2]})
                    elif trace_step[1] == ADD:
                        ec += '''
        {s}self.stack[-1] += {x}
        {s}self.pc += 2'''.format_map({'s':s,'x':trace_step[2]})
                    elif trace_step[1] == PUSH:
                        ec += '''
        {s}self.stack.append({x})
        {s}self.pc += 2'''.format_map({'s':s,'x':trace_step[2]})
                    elif trace_step[1] == POP:
                        ec += '''
        {s}self.stack.pop()
        {s}self.pc += 1'''.format_map({'s':s})

                elif trace_step[0] == TRACE_GUARD_GT:
                    ec += '''
        {s}if self.stack[-1] > {c}:'''.format_map({'s':s,'c':trace_step[1]})
                    ec += inner(trace_step[2], s+'    ', p+[i, 2])
                    ec += '''
        {s}else:'''.format_map({'s':s})
                    ec += inner(trace_step[3], s+'    ', p+[i, 3])

                elif trace_step[0] == TRACE_ENTER_TRACE:
                    ec += '''
        {s}trace_{x}()'''.format_map({'s':s,'x':trace_step[1]['trace_id']})
                else:
                    raise UnknownTraceRecordError()

            return ec

        ec += inner(trace)
        return ec

    def print_state(self):
        print("State is pc =", self.pc, "stack =", self.stack)
        #print("JITted scope =", self.jitted_code_scope)

    def enter_trace(self, loop_info):
        #print('enter_trace:', loop_info['executable_trace'])
        exec(loop_info['executable_trace'], self.jitted_code_scope) # defines the trace in the jitted context
        exec('trace_%d()' % (loop_info['trace_id']), self.jitted_code_scope)

    def run_JUMP(self):
        old_pc = self.pc
        new_pc = self.code[self.pc+1]

        if new_pc < old_pc:
            if (new_pc, old_pc) in self.loops:
                loop_info = self.loops[(new_pc, old_pc)]

                loop_info['hotness'] += 1

                if loop_info['has_trace']:
                    Interpreter.run_JUMP(self) # run the jump, then run the trace
                    #print("Running previously-compiled trace for loop", new_pc, "-",  old_pc)
                    print("Starting trace", new_pc, '-', old_pc)
                    self.print_state()
                    try:
                        self.enter_trace(loop_info)
                        # can a trace leave normally? no, it is an infinite loop
                    except GuardFailed as e:
                        print("Guard failed after", e.count, "iterations, leaving trace for interpreter execution")
                        self.print_state()
                        # Trace execution was not good for this iteration, so, fallback to RECORDING interpreter
                        # the jitted code is modifying interpreter state, no need to sync
                        print("Recording after guard")
                        self.recording_trace = True
                        recording_interpreter = RecordingInterpreter(self.pc, self.stack, self.code, self.loops, self.recording_trace, old_pc)
                        recording_interpreter.trace = loop_info['trace']
                        parent_if = navigate_inner(e.path[0:-1], recording_interpreter.trace)
                        assert parent_if[0] == TRACE_GUARD_GT
                        inner = []
                        parent_if[e.path[-1]] = inner
                        recording_interpreter.inner = inner
                        try:
                            recording_interpreter.interpret()
                            raise Halted()
                        except TraceRecordingEnded:
                            self.pc = recording_interpreter.pc
                            self.recording_trace = False
                            # get rid of the duplicate conditional due to restarting the trace
                            assert inner[0][0] == TRACE_GUARD_GT
                            new_child = inner[0][e.path[-1]]
                            other_child = parent_if[3 if e.path[-1] == 2 else 2]
                            left, right = (new_child, other_child) if e.path[-1] == 2 else (other_child, new_child)
                            parent_if[2] = left
                            parent_if[3] = right
                            loop_info['executable_trace'] = self.translate_trace(loop_info)
                            print("Recompiled execution trace:", loop_info['executable_trace'])
                            TracingInterpreter.run_JUMP(self)
                            return

                if loop_info['hotness'] > 10 and loop_info['has_trace'] == False:
                    if not self.recording_trace:
                        print("Found new hot loop from", new_pc, "to", old_pc, "(included)")
                        self.recording_trace = True

                        Interpreter.run_JUMP(self) # run the jump normally so that we start the trace at the beginning of the loop
                        recording_interpreter = RecordingInterpreter(self.pc, self.stack, self.code, self.loops, self.recording_trace, old_pc)
                        try:
                            print("Trace recording started at pc =", new_pc, "until (included) pc =", old_pc)
                            recording_interpreter.interpret()
                            raise Halted()
                        except TraceRecordingEnded:
                            print("Trace recording ended!")
                            self.pc = recording_interpreter.pc # the rest are mutable datastructures that were shared with the recording interp
                            self.recording_trace = False

                            loop_info['trace_id'], loop_info['trace'] = self.trace_id, recording_interpreter.trace
                            self.trace_id += 1
                            loop_info['has_trace'], loop_info['executable_trace'] =  True, self.translate_trace(loop_info)
                            print("Execution trace:", loop_info['executable_trace'])
                            print("Now jumping into compiled trace!")
                            TracingInterpreter.run_JUMP(self) # recursive call, but this time it will run the compiled trace
                            return

            else:
                self.loops[(new_pc, old_pc)] = {'hotness': 1, 'has_trace': False}
                self.recording_trace = False

        Interpreter.run_JUMP(self)

class TraceRecordingEnded(Exception):
    pass

TRACE_INSTR, TRACE_GUARD_GT, TRACE_ENTER_TRACE  = range(3)

class GuardFailed(Exception):
    def __init__(self, count, path):
        self.count = count
        self.path = path

def navigate_inner(path, trace):
    if path==[]:
        return trace
    else:
        return navigate_inner(path[1:], trace[path[0]])

class RecordingInterpreter(TracingInterpreter):
    def __init__(self, pc, stack, code, loops, recording_trace, end_of_trace):
        self.trace = []
        self.inner = self.trace
        self.end_of_trace = end_of_trace

        TracingInterpreter.__init__(self, pc, stack, code, loops, recording_trace)

    def is_end_of_trace(self, current_pc):
        return current_pc == self.end_of_trace

    def run_PUSH(self):
        #print("Recording PUSH")
        self.inner.append( (TRACE_INSTR, self.code[self.pc], self.code[self.pc+1]) )
        TracingInterpreter.run_PUSH(self)

    def run_ADD(self):
        #print("Recording ADD")
        self.inner.append( (TRACE_INSTR, self.code[self.pc], self.code[self.pc+1]) )
        TracingInterpreter.run_ADD(self)

    def run_GT(self):
        #print("Recording GT")

        if self.stack[-1] > self.code[self.pc+1]:
            inner = [ (TRACE_INSTR, JUMP, self.code[self.pc+2]) ]
            left = inner
            right = None
        else:
            inner = [ (TRACE_INSTR, JUMP, self.pc+3) ]
            left = None
            right = inner
        self.inner.append( [TRACE_GUARD_GT, self.code[self.pc+1], left, right] )
        self.inner = inner

        TracingInterpreter.run_GT(self)

    def run_JUMP(self):
        end_of_trace = self.is_end_of_trace(self.pc)
        #print("Recording JUMP")
        self.inner.append( (TRACE_INSTR, self.code[self.pc], self.code[self.pc+1]) )
        if end_of_trace:
            raise TraceRecordingEnded()

        TracingInterpreter.run_JUMP(self)

    def run_POP(self):
        #print("Recording POP")
        self.inner.append( (TRACE_INSTR, POP))
        TracingInterpreter.run_POP(self)

    def enter_trace(self, loop_info):
        #print("Recording ENTER_TRACE")
        self.inner.append( (TRACE_ENTER_TRACE, loop_info) )
        TracingInterpreter.enter_trace(self, loop_info)

class Halted(Exception):
    pass

def interpret(code):
    interpreter = TracingInterpreter(0, [], code, {}, False)
    try:
        return interpreter.interpret()
    except Halted:
        return interpreter.stack[-1]

from examples import examples
for (title, code, expected) in examples:
    print("# Example", title)
    res = interpret(code)
    assert expected == res, "in example %s, expected %d, got %d" % (title, expected, res)
