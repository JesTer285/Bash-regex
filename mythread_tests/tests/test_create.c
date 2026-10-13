#include "mythread.h"
#include "test.h"
#include <stdint.h>
#include <string.h>

static void *worker_noop(void *arg) {
	(void)arg;
	return NULL;
}

static void *worker_returns_arg(void *arg) {
	return arg;
}

static void *worker_returns_42(void *arg) {
	(void)arg;
	return (void *)(intptr_t)42;
}

struct slot { int value; };

static void *worker_write_slot(void *arg) {
	struct slot *s = (struct slot *)arg;
	s->value = 42;
	return NULL;
}

int test_create_basic(void) {
	mythread_t t;
	ASSERT_SUCCESS(mythread_create(&t, NULL, worker_noop, NULL));
	ASSERT_SUCCESS(mythread_join(t, NULL));
	return TEST_SUCCESS;
}

int test_create_argument(void) {
	mythread_t t;
	int value = 12345;
	ASSERT_SUCCESS(mythread_create(&t, NULL, worker_returns_arg, &value));

	void *ret = NULL;
	ASSERT_SUCCESS(mythread_join(t, &ret));
	ASSERT_TRUE(ret == &value);
	return TEST_SUCCESS;
}

int test_create_return_value(void) {
	mythread_t t;
	ASSERT_SUCCESS(mythread_create(&t, NULL, worker_returns_42, NULL));

	void *ret = NULL;
	ASSERT_SUCCESS(mythread_join(t, &ret));
	ASSERT_EQ((intptr_t)ret, 42);
	return TEST_SUCCESS;
}

int test_create_multiple(void) {
	const unsigned N = 8;
	mythread_t t[N];

	for (int i = 0; i < N; ++i) {
		ASSERT_SUCCESS(mythread_create(&t[i], NULL, worker_noop, NULL));
	}
	for (int i = 0; i < N; ++i) {
		ASSERT_SUCCESS(mythread_join(t[i], NULL));
	}
	return TEST_SUCCESS;
}

int test_create_shared_memory(void) {
	const unsigned N = 16;
	struct slot slots[N];
	mythread_t t[N];
	memset(slots, 0, sizeof(slots));

	for (int i = 0; i < N; ++i) {
		ASSERT_SUCCESS(mythread_create(&t[i], NULL, worker_write_slot, &slots[i]));
	}
	for (int i = 0; i < N; ++i) {
		ASSERT_SUCCESS(mythread_join(t[i], NULL));
	}
	for (int i = 0; i < N; ++i) {
		ASSERT_EQ(slots[i].value, 42);
	}
	return TEST_SUCCESS;
}
