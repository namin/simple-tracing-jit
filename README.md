This project builds a simple, easy to understand interpreter with a tracing JIT.
Tracing is a technique for improving the performance of interpreters and VMs described by Gal et al. ([2006](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.113.557&rep=rep1&type=pdf), [2007](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.85.2412&rep=rep1&type=pdf)).
This technique has been implemented in PyPy [[Bolz et al., 2009](https://dl.acm.org/doi/10.1145/1565824.1565827)], Mozilla Firefox [[Gal et al., 2009](https://dl.acm.org/doi/10.1145/1543135.1542528)] and LuaJIT.

## TODOs / Limitations

- [ ] We can keep entering traces while recording after failure, going deeper and deeper into recordings.

- [ ] When recording after a guard fails, backjumps are not accounted for as hot loops.

- [x] Find a program that requires more than one trace in the tree tracing JIT.

- [x] Does not implement any heuristics to stop recording once in a hot loop.

- [ ] Does not JIT conditional jumps, see `one_simple_loop2`.

### Can be solved with Trace Trees

- [x] For nested loops, the outer loop keeps being re-entered rather than entered once. This is because the inner exception bubbles up to the top.

- [x] A loop is not recompiled even though a new path becomes hot, see `nested_loops2`.
