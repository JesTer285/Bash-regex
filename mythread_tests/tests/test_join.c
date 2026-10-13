#include "mythread.h"
#include "test.h"
#include <stdint.h>

static void *worker_null(void *arg) { (void)arg; return NULL; }
static void *worker_ret (void *arg) { return arg; }

int test_join_null_retval(void) {
	mythread_t t;
	ASSERT_SUCCESS(mythread_create(&t, NULL, worker_null, NULL));
	ASSERT_SUCCESS(mythread_join(t, NULL));   /* retval == NULL допустим */
	return TEST_SUCCESS;
}

int test_join_retval(void) {
	mythread_t t;
	int x = 7;
	ASSERT_SUCCESS(mythread_create(&t, NULL, worker_ret, &x));

	void *ret = NULL;
	ASSERT_SUCCESS(mythread_join(t, &ret));
	ASSERT_TRUE(ret == &x);
	return TEST_SUCCESS;
}

int test_join_multiple(void) {
	enum { N = 4 };
	mythread_t t[N];
	int vals[N];

	for (int i = 0; i < N; ++i) {
		vals[i] = i * 100;
		ASSERT_SUCCESS(mythread_create(&t[i], NULL, worker_ret, &vals[i]));
	}
	for (int i = 0; i < N; ++i) {
		void *ret = NULL;
		ASSERT_SUCCESS(mythread_join(t[i], &ret));
		ASSERT_TRUE(ret == &vals[i]);
	}
	return TEST_SUCCESS;
}
