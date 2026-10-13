#ifndef TEST_H
#define TEST_H

#include <stdio.h>
#include <stdint.h>

#include "runner.h"   /* for TEST_SUCCESS / TEST_FAILURE */

#define ASSERT_TRUE(cond) do {                                      \
	if (!(cond)) {                                                   \
		fprintf(stderr, "  ASSERT_TRUE(%s) failed at %s:%d\n",      \
				#cond, __FILE__, __LINE__);                         \
		return TEST_FAILURE;                                        \
	}                                                               \
} while (0)

#define ASSERT_EQ(a, b) do {                                        \
	int64_t _a = (int64_t)(a);                                      \
	int64_t _b = (int64_t)(b);                                      \
	if (_a != _b) {                                                 \
		fprintf(stderr,                                             \
				"  ASSERT_EQ(%s, %s) failed: %lld != %lld at %s:%d\n", \
				#a, #b, (long long)_a, (long long)_b,              \
				__FILE__, __LINE__);                                \
		return TEST_FAILURE;                                        \
	}                                                               \
} while (0)

#define ASSERT_NULL(p) do {                                         \
	if ((p) != NULL) {                                              \
		fprintf(stderr, "  ASSERT_NULL(%s) failed at %s:%d\n",     \
				#p, __FILE__, __LINE__);                            \
		return TEST_FAILURE;                                        \
	}                                                               \
} while (0)

#define ASSERT_NOT_NULL(p) do {                                     \
	if ((p) == NULL) {                                              \
		fprintf(stderr, "  ASSERT_NOT_NULL(%s) failed at %s:%d\n", \
				#p, __FILE__, __LINE__);                            \
		return TEST_FAILURE;                                        \
	}                                                               \
} while (0)

#define ASSERT_SUCCESS(expr) do {                                   \
	int _r = (int)(expr);                                           \
	if (_r != 0) {                                                  \
		fprintf(stderr, "  ASSERT_SUCCESS(%s) failed: ret=%d at %s:%d\n", \
				#expr, _r, __FILE__, __LINE__);                     \
		return TEST_FAILURE;                                        \
	}                                                               \
} while (0)

#define ASSERT_FAILURE(expr) do {                                   \
	int _r = (int)(expr);                                           \
	if (_r == 0) {                                                  \
		fprintf(stderr, "  ASSERT_FAILURE(%s) failed: ret=0 at %s:%d\n", \
				#expr, __FILE__, __LINE__);                         \
		return TEST_FAILURE;                                        \
	}                                                               \
} while (0)

#endif
