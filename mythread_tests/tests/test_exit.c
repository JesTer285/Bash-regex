#include "mythread.h"
#include "test.h"
#include <stdint.h>

static void *worker_exit_null(void *arg) {
	(void)arg;
	mythread_exit(NULL);
	/* недостижимо для корректной реализации */
	return (void *)(intptr_t)1;
}

static void *worker_exit_retval(void *arg) {
	(void)arg;
	mythread_exit((void *)(intptr_t)99);
	return NULL;
}

static void *worker_touch_after_exit(void *arg) {
	(void)arg;
	mythread_exit(NULL);
	/* Намеренно пишем в невалидный адрес: если mythread_exit вернётся,
	   тест упадёт по SIGSEGV, что мы и ловим в runner'е. */
	*(volatile int *)0 = 0xC0FFEE;
	return NULL;
}

int test_exit_null(void) {
	mythread_t t;
	ASSERT_SUCCESS(mythread_create(&t, NULL, worker_exit_null, NULL));

	void *ret = (void *)(intptr_t)0xdeadbeef;
	ASSERT_SUCCESS(mythread_join(t, &ret));
	ASSERT_NULL(ret);
	return TEST_SUCCESS;
}

int test_exit_retval(void) {
	mythread_t t;
	ASSERT_SUCCESS(mythread_create(&t, NULL, worker_exit_retval, NULL));

	void *ret = NULL;
	ASSERT_SUCCESS(mythread_join(t, &ret));
	ASSERT_EQ((intptr_t)ret, 99);
	return TEST_SUCCESS;
}

int test_exit_stops_thread(void) {
	mythread_t t;
	ASSERT_SUCCESS(mythread_create(&t, NULL, worker_touch_after_exit, NULL));
	ASSERT_SUCCESS(mythread_join(t, NULL));
	return TEST_SUCCESS;
}
