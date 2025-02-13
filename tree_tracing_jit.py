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
        id = loop_info['trace_id']
        # create python code to run the trace
        executable_trace = f'''
def trace_{id}():
    count = 0
    while True:
        count += 1
        print('in trace_{id}, iteration '+str(count))
'''
        def inner(trace, s='', p=[]):
            executable_trace = ''
            if trace is None:
                executable_trace += f'''
        {s}raise GuardFailed({id}, count, {p})'''
                return executable_trace
            for (i, trace_step) in enumerate(trace):
                if trace_step[0] == TRACE_INSTR:
                    if trace_step[1] == JUMP:
                        executable_trace += f'''
        {s}self.pc = {trace_step[2]}'''
                    elif trace_step[1] == ADD:
                        executable_trace += f'''
        {s}self.stack[-1] += {trace_step[2]}
        {s}self.pc += 2'''
                    elif trace_step[1] == PUSH:
                        executable_trace += f'''
        {s}self.stack.append({trace_step[2]})
        {s}self.pc += 2'''
                    elif trace_step[1] == POP:
                        executable_trace += f'''
        {s}self.stack.pop()
        {s}self.pc += 1'''

                elif trace_step[0] == TRACE_GUARD_GT:
                    executable_trace += f'''
        {s}if self.stack[-1] > {trace_step[1]}:'''
                    executable_trace += inner(trace_step[2], s+'    ', p+[i, 2])
                    executable_trace += f'''
        {s}else:'''
                    executable_trace += inner(trace_step[3], s+'    ', p+[i, 3])

                elif trace_step[0] == TRACE_ENTER_TRACE:
                    executable_trace += f'''
        {s}trace_{trace_step[1]['trace_id']}()'''
                else:
                    raise UnknownTraceRecordError()

            return executable_trace

        executable_trace += inner(trace)
        return executable_trace

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
                        if self.recording_trace:
                            print("Already recording...")
                            return
                        # TODO: no example exercises this
                        if e.trace_id != loop_info['trace_id']:
                            print("Bubbled up... not recording")
                            return
                        print("Recording after guard")
                        trace = loop_info['trace']
                        parent_if = navigate_inner(e.path[0:-1], trace)
                        assert parent_if[0] == TRACE_GUARD_GT
                        inner = []
                        parent_if[e.path[-1]] = inner
                        if e.path[-1] == 2:
                            # resume on left
                            self.pc = self.code[self.pc+2]
                        else:
                            # resume on right
                            assert e.path[-1] == 3
                            self.pc = self.pc + 3
                        inner.append((TRACE_INSTR, JUMP, self.pc))

                        self.recording_trace = True
                        recording_interpreter = RecordingInterpreter(self.pc, self.stack, self.code, self.loops, self.recording_trace, old_pc)
                        recording_interpreter.trace = trace
                        recording_interpreter.inner = inner
                        try:
                            recording_interpreter.interpret()
                            return
                        except TraceRecordingEnded:
                            self.pc = recording_interpreter.pc
                            self.recording_trace = False
                            loop_info['executable_trace'] = self.translate_trace(loop_info)
                            print("Recompiled execution trace:", loop_info['executable_trace'])
                            TracingInterpreter.run_JUMP(self)
                            return
                        except AbandonedTrace:
                            print("Trace abandoned")
                            self.pc = recording_interpreter.pc
                            self.recording_trace = False
                            self.print_state()
                            parent_if[e.path[-1]] = None
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
                            return
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
                        except AbandonedTrace:
                            print("Trace abandoned")
                            self.pc = recording_interpreter.pc
                            self.recording_trace = False
                            return

            else:
                self.loops[(new_pc, old_pc)] = {'hotness': 1, 'has_trace': False}
                self.recording_trace = False

        Interpreter.run_JUMP(self)

class TraceRecordingEnded(Exception):
    pass

TRACE_INSTR, TRACE_GUARD_GT, TRACE_ENTER_TRACE  = range(3)

class GuardFailed(Exception):
    def __init__(self, trace_id, count, path):
        self.trace_id = trace_id
        self.count = count
        self.path = path

def navigate_inner(path, trace):
    if path==[]:
        return trace
    else:
        return navigate_inner(path[1:], trace[path[0]])

class AbandonedTrace(Exception):
    pass

class RecordingInterpreter(TracingInterpreter):
    def __init__(self, pc, stack, code, loops, recording_trace, end_of_trace):
        self.trace = []
        self.inner = self.trace
        self.end_of_trace = end_of_trace
        self.n_backjumps = 0
        self.n_steps = 0

        TracingInterpreter.__init__(self, pc, stack, code, loops, recording_trace)

    def is_end_of_trace(self, current_pc):
        return current_pc == self.end_of_trace

    def maybe_abandon_trace(self, current_pc, next_pc):
        if next_pc < current_pc:
            self.n_backjumps += 1
        if self.n_backjumps > 3:
            print("Too many recorded backjumps")
            raise AbandonedTrace()

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
        next_pc = self.code[self.pc+1]
        self.inner.append( (TRACE_INSTR, self.code[self.pc], next_pc) )
        if end_of_trace:
            raise TraceRecordingEnded()
        self.maybe_abandon_trace(self.pc, next_pc)

        TracingInterpreter.run_JUMP(self)

    def run_POP(self):
        #print("Recording POP")
        self.inner.append( (TRACE_INSTR, POP))
        TracingInterpreter.run_POP(self)

    def enter_trace(self, loop_info):
        #print("Recording ENTER_TRACE")
        self.inner.append( (TRACE_ENTER_TRACE, loop_info) )
        TracingInterpreter.enter_trace(self, loop_info)

    def at_each_step(self):
        TracingInterpreter.at_each_step(self)
        self.n_steps += 1
        if self.n_steps > 10:
            print("Too many steps")
            raise AbandonedTrace()

def interpret(code):
    return TracingInterpreter(0, [], code, {}, False).interpret()

if __name__ == '__main__':
    import examples
    examples.run(interpret)
