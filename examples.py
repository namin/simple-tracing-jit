from simple_language import *

one_simple_loop = [
    PUSH, 0,     # 0
    GT, 50000, 9, # 2
    ADD, 1,       # 5
    JUMP, 2,      # 7
    HALT         # 9
]

one_simple_loop1 = [
    PUSH, 0,     # 0
    GT, 10, 9, # 2
    ADD, 1,       # 5
    JUMP, 2,      # 7
    HALT         # 9
]

two_simple_loops = [
    PUSH, 0,     # 0
    GT, 50000, 9, # 2
    ADD, 1,       # 5
    JUMP, 2,      # 7

    GT, 100000, 16, # 9
    ADD, 2,         # 12
    JUMP, 9,        # 14

    HALT         # 16
]

nested_loops = [
    PUSH, 0,     # 0 - outer loop counter
    GT, 30, 19, # 2 - start of outer loop
    PUSH, 0,     # 5 - inner loop counter
    GT, 15, 14,  # 7 - start of inner loop
    ADD, 1,      # 10
    JUMP, 7,     # 12 - end of inner loop
    POP,         # 14
    ADD, 2,      # 15
    JUMP, 2,      # 17 - end of outer loop

    HALT         # 19
]

nested_loops1 = [
    PUSH, 0,     # 0 - outer loop counter
    GT, 30, 19, # 2 - start of outer loop
    PUSH, 0,     # 5 - inner loop counter
    GT, 10, 14,  # 7 - start of inner loop
    ADD, 1,      # 10
    JUMP, 7,     # 12 - end of inner loop
    POP,         # 14
    ADD, 2,      # 15
    JUMP, 2,      # 17 - end of outer loop

    HALT         # 19
]

nested_loops2 = [
    PUSH, 0,     # 0 - outer loop counter
    GT, 70, 22, # 2 - start of outer loop
    GT, 24, 18, # +3
    PUSH, 0,     # 5+3 - inner loop counter
    GT, 15, 17,  # 7+3 - start of inner loop
    ADD, 1,      # 10+3
    JUMP, 10,     # 12+3 - end of inner loop
    POP,         # 14+3
    ADD, 2,      # 15+3
    JUMP, 2,      # 17+3 - end of outer loop

    HALT         # 19+3
]

nested_double_loops = [
    PUSH, 0,   # 0
    GT, 20, 29,# 2
    PUSH, 0,   # 5
    GT, 15, 14,# 7
    ADD, 1,    # 10
    JUMP, 7,   # 12
    POP,       # 14
    PUSH, 0,   # 15
    GT, 20, 24,# 17
    ADD, 1,    # 20
    JUMP, 17,  # 22
    POP,       # 24
    ADD, 1,    # 25
    JUMP, 2,   # 27
    HALT       # 29
]

examples = [
    ("1", one_simple_loop, 50001),
    ("1a", one_simple_loop1, 11),
    ("2", two_simple_loops, 100001),
    ("3", nested_loops, 32),
    ("3a", nested_loops1, 32),
    ("3b", nested_loops2, 72),
    ("4", nested_double_loops, 21)
]
