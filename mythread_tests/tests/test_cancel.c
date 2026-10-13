#include "mythread.h"
#include "test.h"

static void *worker_spin(void *arg) {
	volatile int *stop = (volatile int *)arg;
	while (!*stop) {
		mythread_yield();
	}
	return NULL;
}

int test_cancel_basic(void) {
	mythread_t t;
	volatile int stop = 0;

	ASSERT_SUCCESS(mythread_create(&t, NULL, worker_spin, (void *)&stop));
	ASSERT_SUCCESS(mythread_cancel(t));

	stop = 1;                               /* подстраховка, если cancel deferred */
	ASSERT_SUCCESS(mythread_join(t, NULL));
	return TEST_SUCCESS;
}

int test_cancel_deferred(void) {
	mythread_t t;
	volatile int stop = 0;

	ASSERT_SUCCESS(mythread_create(&t, NULL, worker_spin, (void *)&stop));

	/* Дать потоку немного пожить, потом отменить. */
	for (volatile int i = 0; i < 1000; ++i) {
		mythread_yield();
	}
	ASSERT_SUCCESS(mythread_cancel(t));
	ASSERT_SUCCESS(mythread_join(t, NULL));

	stop = 1;
	return TEST_SUCCESS;
}
