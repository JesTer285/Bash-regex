#include "runner.h"
#include "optional.h"
#include "colors.h"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>

#define DEFAULT_TIMEOUT_MS 5000

static int run_one(const test_case_t *t)
{
	int timeout = t->timeout_ms ? t->timeout_ms : DEFAULT_TIMEOUT_MS;

	pid_t pid = fork();
	if (pid < 0) {
		perror("fork");
		return TEST_FAILURE;
	}

	if (pid == 0) {
		/* Child: run the test */
		_exit(t->fn());
	}

	/* Parent: wait with timeout */
	int waited = 0;
	int status = 0;

	while (waited < timeout) {
		pid_t r = waitpid(pid, &status, WNOHANG);
		if (r == pid) {
			if (WIFEXITED(status))
				return WEXITSTATUS(status);
			return TEST_FAILURE;   /* died from signal */
		}
		usleep(10 * 1000);
		waited += 10;
	}

	fprintf(stderr, "TIMEOUT after %d ms — killing pid %d\n", timeout, pid);
	kill(pid, SIGKILL);
	waitpid(pid, &status, 0);
	return TEST_FAILURE;
}

int run_all(const test_case_t *tests, int n)
{
	int passed = 0, failed = 0, skipped = 0;

	for (int i = 0; i < n; ++i) {
		const test_case_t *t = &tests[i];

		if (t->optional && !feature_available(t->name)) {
			printf("SKIP %s (feature not available)\n", t->name);
			skipped++;
			continue;
		}

		printf("RUN %s ... ", t->name);
		fflush(stdout);

		if (run_one(t) == TEST_SUCCESS) {
			printf(COLOR_GREEN "OK" COLOR_RESET "\n");
			passed++;
		} else {
			printf(COLOR_RED "FAIL" COLOR_RESET "\n");
			failed++;
		}
	}

	printf("\npassed: %d, failed: %d, skipped: %d\n",
		   passed, failed, skipped);
	return failed == 0 ? 0 : 1;
}
