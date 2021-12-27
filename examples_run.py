from examples import examples
import simple_interpreter
import simple_tracing_jit

for (title, code, expected) in examples:
    print("# Example", title)
    res1 = simple_interpreter.interpret(code)
    assert expected == res1, "in example %s, expected %d, got %d" % (title, expected, res1)
    res2 = simple_tracing_jit.interpret(code)
    assert expected == res2, "in example %s, expected %d, got %d" % (title, expected, res2)
