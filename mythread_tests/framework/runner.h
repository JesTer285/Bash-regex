#ifndef RUNNER_H
#define RUNNER_H

typedef int (*test_fn_t)(void);

typedef struct {
    const char *name;
    test_fn_t   fn;
    int         timeout_ms;   /* 0 by default */
    int         optional;     /* optional features are defined with weak symbols */
} test_case_t;

#define TEST_SUCCESS 0
#define TEST_FAILURE 1

int run_all(const test_case_t *tests, int n);

#endif
