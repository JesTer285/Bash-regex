CC      ?= gcc
CFLAGS  ?= -std=c11 -Wall -Wextra -O2 -g
LDFLAGS ?= -lpthread
IMPL    ?= reference

ifeq ($(IMPL),reference)
  IMPL_DIR := impl/reference
  IMPL_SRC := impl/reference/mythread.c
  IMPL_LIB :=
else ifeq ($(IMPL),custom)
  IMPL_DIR := impl/custom
  IMPL_SRC := $(wildcard impl/custom/*.c)
  IMPL_LIB := $(wildcard impl/custom/*.a)
else
  $(error Unknown IMPL=$(IMPL))
endif

CFLAGS += -I$(IMPL_DIR) -Iinclude -Iframework -Itests

SRC := \
    main.c \
    framework/runner.c \
    framework/optional.c \
    tests/test_create.c \
    tests/test_join.c \
    tests/test_detach.c \
    tests/test_exit.c \
    tests/test_cancel.c \
    tests/test_stress.c \
    $(IMPL_SRC)

mythread_tests: $(SRC)
	$(CC) $(CFLAGS) $^ $(IMPL_LIB) -o $@ $(LDFLAGS)

check-reference: mythread_tests
	./mythread_tests

check-custom:
	$(MAKE) clean
	$(MAKE) IMPL=custom mythread_tests
	./mythread_tests

clean:
	rm -f mythread_tests

.PHONY: check-reference check-custom clean
