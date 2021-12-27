This project builds a simple, easy to understand interpreter with a tracing JIT.
Tracing is a technique for improving the performance of interpreters and VMs described by Gal et al. ([2006](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.113.557&rep=rep1&type=pdf), [2007](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.85.2412&rep=rep1&type=pdf)).
This technique has been implemented in PyPy [[Bolz et al., 2009](https://dl.acm.org/doi/10.1145/1565824.1565827)], Mozilla Firefox [[Gal et al., 2009](https://dl.acm.org/doi/10.1145/1543135.1542528)] and LuaJIT.

## TODOs / Limitations

- [ ] For nested loops, the outer loop keeps being re-entered rather than entered once. This is because the inner exception bubbles up to the top. Is this standard? Maybe relevant [2013 paper](https://dl.acm.org/doi/10.1145/2480360.2384586).
