#include "optional.h"
#include <string.h>

int feature_available(const char *test_name) {
    if (strncmp(test_name, "cancel_", 7) == 0)
        return mythread_cancel != NULL;
    if (strncmp(test_name, "yield_", 6) == 0)
        return mythread_yield != NULL;
    return 1;
}
