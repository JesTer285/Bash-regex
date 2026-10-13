#include "runner.h"
#include "test.h"
#include <stddef.h>

#define TIMEOUT 3000

/* create */
int test_create_basic(void);
int test_create_argument(void);
int test_create_return_value(void);
int test_create_multiple(void);
int test_create_shared_memory(void);

/* join */
int test_join_null_retval(void);
int test_join_retval(void);
int test_join_multiple(void);

/* detach */
int test_detach_basic(void);
int test_detach_multiple(void);

/* exit */
int test_exit_null(void);
int test_exit_retval(void);
int test_exit_stops_thread(void);

/* cancel (optional) */
int test_cancel_basic(void);
int test_cancel_deferred(void);

/* stress */
int test_stress_many_threads(void);
int test_stress_churn(void);

int main(void) {
	const test_case_t tests[] = {
		{"create_basic",         test_create_basic,         TIMEOUT, 0},
		{"create_argument",      test_create_argument,      TIMEOUT, 0},
		{"create_return_value",  test_create_return_value,  TIMEOUT, 0},
		{"create_multiple",      test_create_multiple,      TIMEOUT, 0},
		{"create_shared_memory", test_create_shared_memory, TIMEOUT, 0},

		{"join_null_retval",     test_join_null_retval,     TIMEOUT, 0},
		{"join_retval",          test_join_retval,          TIMEOUT, 0},
		{"join_multiple",        test_join_multiple,        TIMEOUT, 0},

		{"detach_basic",         test_detach_basic,         TIMEOUT, 0},
		{"detach_multiple",      test_detach_multiple,      TIMEOUT, 0},

		{"exit_null",            test_exit_null,            TIMEOUT, 0},
		{"exit_retval",          test_exit_retval,          TIMEOUT, 0},
		{"exit_stops_thread",    test_exit_stops_thread,    TIMEOUT, 0},

		{"cancel_basic",         test_cancel_basic,         TIMEOUT, 1},
		{"cancel_deferred",      test_cancel_deferred,      TIMEOUT, 1},

		{"stress_many_threads",  test_stress_many_threads,  TIMEOUT, 0},
		{"stress_churn",         test_stress_churn,         TIMEOUT, 0},
	};
	const int n = (int)(sizeof(tests) / sizeof(tests[0]));
	return run_all(tests, n);
}
