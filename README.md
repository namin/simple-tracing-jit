This project builds a simple, easy to understand interpreter with a tracing JIT.
Tracing is a technique for improving the performance of interpreters and VMs described by Gal et al. ([2006](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.113.557&rep=rep1&type=pdf), [2007](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.85.2412&rep=rep1&type=pdf)).
This technique has been implemented in PyPy [[Bolz et al., 2009](https://dl.acm.org/doi/10.1145/1565824.1565827)], Mozilla Firefox [[Gal et al., 2009](https://dl.acm.org/doi/10.1145/1543135.1542528)] and LuaJIT.

## ToC

- [`simple_language`](simple_language.py): keywords for the simple stack-based language.

- [`examples`](examples.py): example programs.

- [`simple_interpreter`](simple_interpreter.py): a simple interpreter.
  It loops until `HALT`, one command at a time.

- [`simple_tracing_jit`](simple_tracing_jit.py): a simple JIT tracing interpreter.
  It detects hot loops by backjumps, records a trace, generates direct Python code, executes it when reaching the loop again, resumes interpreted execution when failing on a guard.
  It does not extend or recompute a trace even when the execution keeps failing on a guard.
- [`tree_tracing_jit`](tree_tracing_jit.py): a tree-tracing interpreter following on Gal et al. (2006).
  It resumes recording after a guard failure, completing the trace in a tree-like fashion.

## Running

The code is in Python 3.
The command `python <FILE>` runs the examples specifically for file `<FILE>`.
The command `python examples.py` runs all examples on all interpreters.
