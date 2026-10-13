#include "mythread.h"
#include "test.h"

static void *worker_inc(void *arg) {
	int *p = (int *)arg;
	__atomic_fetch_add(p, 1, __ATOMIC_SEQ_CST);
	return NULL;
}

int test_stress_many_threads(void) {
	enum { N = 64 };
	static int counter;
	counter = 0;

	mythread_t t[N];
	for (int i = 0; i < N; ++i) {
		ASSERT_SUCCESS(mythread_create(&t[i], NULL, worker_inc, &counter));
	}
	for (int i = 0; i < N; ++i) {
		ASSERT_SUCCESS(mythread_join(t[i], NULL));
	}
	ASSERT_EQ(counter, N);
	return TEST_SUCCESS;
}

int test_stress_churn(void) {
	static int counter;
	counter = 0;

	for (int round = 0; round < 20; ++round) {
		mythread_t t;
		ASSERT_SUCCESS(mythread_create(&t, NULL, worker_inc, &counter));
		ASSERT_SUCCESS(mythread_join(t, NULL));
	}
	ASSERT_EQ(counter, 20);
	return TEST_SUCCESS;
}
