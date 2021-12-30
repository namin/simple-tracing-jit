# TODOs / Limitations

- [ ] If we fail in a trace inside a trace, we bubble up to the outer trace and record from there. This seems wrong.

- [ ] When recording after a guard fails, backjumps are not accounted for as hot loops.

- [x] We can keep entering traces while recording after failure, going deeper and deeper into recordings.

- [x] Find a program that requires more than one trace in the tree tracing JIT.

- [x] Does not implement any heuristics to stop recording once in a hot loop.

- [ ] Does not JIT conditional jumps, see `one_simple_loop2`.

## Can be solved with Trace Trees

- [x] For nested loops, the outer loop keeps being re-entered rather than entered once. This is because the inner exception bubbles up to the top.

- [x] A loop is not recompiled even though a new path becomes hot, see `nested_loops2`.
