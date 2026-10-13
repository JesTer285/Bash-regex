#include "mythread.h"
#include "test.h"

static void *worker_noop(void *arg) { (void)arg; return NULL; }

int test_detach_basic(void) {
	mythread_t t;
	ASSERT_SUCCESS(mythread_create(&t, NULL, worker_noop, NULL));
	ASSERT_SUCCESS(mythread_detach(t));
	return TEST_SUCCESS;
}

int test_detach_multiple(void) {
	enum { N = 8 };
	mythread_t t[N];

	for (int i = 0; i < N; ++i) {
		ASSERT_SUCCESS(mythread_create(&t[i], NULL, worker_noop, NULL));
		ASSERT_SUCCESS(mythread_detach(t[i]));
	}
	return TEST_SUCCESS;
}
