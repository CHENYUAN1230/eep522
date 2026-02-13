#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <string.h>

/*
TARGET_FPS defines the desired frame rate.
TEST_DURATION defines how long (in seconds) the test runs.
*/
#define TARGET_FPS 30
#define TEST_DURATION 5

int main()
{
    struct timespec prev, now;

    /*
    Expected time interval between frames.
    For 30 FPS → 1/30 ≈ 0.033333 seconds.
    */
    double interval = 1.0 / TARGET_FPS;

    clock_gettime(CLOCK_MONOTONIC, &prev);

    double max_jitter = 0;
    double min_jitter = 1000;
    double total_jitter = 0;
    int count = 0;

    while (1)
    {
        usleep(1000000 / TARGET_FPS);

        clock_gettime(CLOCK_MONOTONIC, &now);

        double elapsed =
            (now.tv_sec - prev.tv_sec) +
            (now.tv_nsec - prev.tv_nsec) / 1e9;

        double jitter = elapsed - interval;

        if (jitter > max_jitter)
            max_jitter = jitter;

        if (jitter < min_jitter)
            min_jitter = jitter;

        total_jitter += jitter;
        count++;

        prev = now;

        if (count >= TARGET_FPS * TEST_DURATION)
            break;
    }

    printf("Target interval: %.6f s\n", interval);
    printf("Max jitter: %.6f s\n", max_jitter);
    printf("Min jitter: %.6f s\n", min_jitter);
    printf("Avg jitter: %.6f s\n", total_jitter / count);
    printf("PID: %d\n", getpid());


    /*
    Read context switch statistics from /proc.
    This shows how often the process was switched
    by the Linux scheduler.
    */
    FILE *f = fopen("/proc/self/status", "r");
    if (f) {
        char line[256];
        while (fgets(line, sizeof(line), f)) {
            if (strstr(line, "ctxt"))
                printf("%s", line);
        }
        fclose(f);
    }

    return 0;
}
