#ifndef REFERENCE_MYTHREAD_H
#define REFERENCE_MYTHREAD_H

#include "mythread.h"
#include <pthread.h>
#include <sched.h>

typedef pthread_t mythread_t;

typedef pthread_attr_t mythread_attr_t;

int  mythread_create(mythread_t *thread,
					 const mythread_attr_t *attr,
					 void *(*start_routine)(void *),
					 void *arg);

int  mythread_join(mythread_t thread, void **retval);
int  mythread_detach(mythread_t thread);
void mythread_exit(void *retval);

/* optional */
int  mythread_cancel(mythread_t thread);
int  mythread_yield(void);

#endif
