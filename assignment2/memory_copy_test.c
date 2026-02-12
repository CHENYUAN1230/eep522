#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define KB 1024
#define MB (1024 * KB)

void test_size(size_t size) {
    char *src = malloc(size);
    char *dst = malloc(size);

    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    memcpy(dst, src, size);
    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec) +
                     (end.tv_nsec - start.tv_nsec) / 1e9;

    double bandwidth = size / elapsed / (1024 * 1024);

    printf("Size: %zu bytes | Time: %.6f s | Bandwidth: %.2f MB/s\n",
           size, elapsed, bandwidth);

    free(src);
    free(dst);
}

int main() {
    test_size(1 * KB);
    test_size(1 * MB);
    test_size(100 * MB);
    return 0;
}
