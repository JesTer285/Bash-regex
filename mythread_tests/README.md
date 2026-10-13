# mythread_tests

A standalone test framework for a minimal POSIX-like threading library (`mythread`). It runs each test in a **forked child process** with a configurable timeout, so a crashing or hanging test never takes down the whole suite. Optional features (`mythread_cancel`, `mythread_yield`) are detected at runtime via **weak symbols** and skipped automatically when absent.

---

## Project Structure
```
mythread_tests/
├── include/
│ └── mythread.h 		# Public API
├── impl/
│ ├── reference/ 		# pthread-backed reference implementation
│ │ └── mythread.c
│ └── custom/ 			# Your implementation (mythread.c or libmythread.a)
├── tests/ 				# Individual test suites
│ ├── test_create.c
│ ├── test_join.c
│ ├── test_detach.c
│ ├── test_exit.c
│ ├── test_cancel.c 	# optional
│ └── test_stress.c
├── framework/
│ ├── runner.c 			# fork + timeout per test
│ ├── runner.h
│ ├── test.h 			# Assertion macros
│ ├── optional.c 		# Weak-symbol feature detection
│ ├── optional.h
│ └── colors.h 			# ANSI colour helpers
├── main.c 				# Test registry & entry point
└── Makefile
```

---

## Build & Run

### Reference implementation (pthreads)

```bash
make check-reference
```

### Your custom implementation

Place your mythread.c (or a pre-built libmythread.a) in impl/custom/, then:

```bash
make check-custom
```

### Manual build

```bash
# Reference
make IMPL=reference mythread_tests
./mythread_tests

# Custom
make IMPL=custom mythread_tests
./mythread_tests
```

---

## How it works

1. **Fork-per-test runner (framework/runner.c)**
Each test runs in a child process created with fork(). The parent waits with a timeout (default 5000 ms, per-test override via timeout_ms). If the child doesn't exit in time it is killed with SIGKILL and reported as a failure. Crashes (segfaults, aborts) are also caught as failures.

2. **Optional features (framework/optional.c)**
Symbols mythread_cancel and mythread_yield are declared weak in include/mythread.h. If the implementation doesn't provide them, the linker sets them to NULL. feature_available() checks the symbol pointer and the runner skips tests whose names start with cancel_ or yield_.

---

## Requirements

- GCC or Clang (C11)
- POSIX system (fork, waitpid, usleep)
- pthread for the reference implementation
