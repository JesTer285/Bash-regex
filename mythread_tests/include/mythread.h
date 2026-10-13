#ifndef MYTHREAD_H
#define MYTHREAD_H

#include <stddef.h>

typedef unsigned long mythread_t;
typedef struct mythread_attr mythread_attr_t;

int  mythread_create(mythread_t *thread, const mythread_attr_t *attr,
                     void *(*start_routine)(void *), void *arg);
int  mythread_join  (mythread_t thread, void **retval);
int  mythread_detach(mythread_t thread);
void mythread_exit  (void *retval);

int  mythread_cancel(mythread_t thread) __attribute__((weak));

/* for 1.7 */
int  mythread_yield (void)              __attribute__((weak));

#endif
