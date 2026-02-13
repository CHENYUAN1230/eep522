#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/*
Define memory size units for readability.
KB represents 1024 bytes.
MB represents 1024 * 1024 bytes.
 */
#define KB 1024
#define MB (1024 * KB)

/*
test_size(size)
----------------
This function measures the memory copy performance (bandwidth)
for a given memory size using memcpy().

Steps:
1. Allocate two memory buffers of the specified size.
2. Record the start time using a monotonic clock.
3. Copy memory from src to dst using memcpy().
4. Record the end time.
5. Compute elapsed time and bandwidth (MB/s).
6. Print results.
 */
void test_size(size_t size) 
{

    char *src = malloc(size);
    char *dst = malloc(size);

    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    memcpy(dst, src, size);
    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec) +
                     (end.tv_nsec - start.tv_nsec) / 1e9;

    /*
    Calculate memory bandwidth in MB/s.
    bandwidth = (bytes copied) / (time in seconds)
    Convert bytes to megabytes.
    */
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
    test_size(1000 * MB);
    return 0;
}
