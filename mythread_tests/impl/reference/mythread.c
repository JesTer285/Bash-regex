#include "mythread.h"
#include <pthread.h>

int mythread_create(mythread_t *thread,
					const mythread_attr_t *attr,
					void *(*start_routine)(void *),
					void *arg)
{
	(void)attr;
	if (!thread || !start_routine) return -1;
	return pthread_create((pthread_t *)thread, NULL, start_routine, arg);
}

int mythread_join(mythread_t thread, void **retval)
{
	return pthread_join((pthread_t)thread, retval);
}

int mythread_detach(mythread_t thread)
{
	return pthread_detach((pthread_t)thread);
}

void mythread_exit(void *retval)
{
	pthread_exit(retval);
}

int mythread_cancel(mythread_t thread)
{
	return pthread_cancel((pthread_t)thread);
}

int mythread_yield(void)
{
	return sched_yield();
}
