#ifndef FEATURES_H
#define FEATURES_H

#include "mythread.h"

/* Weak-symbols: if symbols aren't found then linking won't fail */

extern int  mythread_cancel(mythread_t) __attribute__((weak));
extern int  mythread_yield(void)        __attribute__((weak));

int feature_available(const char *test_name);

#endif
