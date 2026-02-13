#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

/*
Assume RGB image format:
Each pixel consists of 3 bytes (R, G, B).
*/
#define BYTES_PER_PIXEL 3

int main(int argc, char *argv[])
{
    /*
    Program usage:
    ./program <width> <height> <fps>
    
    width  = image width in pixels
    height = image height in pixels
    fps    = frames per second
    */
    if (argc != 4)
    {
        printf("Usage: %s <width> <height> <fps>\n", argv[0]);
        return 1;
    }

    int width = atoi(argv[1]);
    int height = atoi(argv[2]);
    int fps = atoi(argv[3]);

    size_t frame_size = width * height * BYTES_PER_PIXEL;

    printf("Resolution: %dx%d\n", width, height);
    printf("FPS: %d\n", fps);
    printf("Frame size: %.2f MB\n", frame_size / (1024.0 * 1024.0));

    uint8_t *frame = malloc(frame_size);
    uint8_t *buffer = malloc(frame_size);

    if (!frame || !buffer)
    {
        printf("Memory allocation failed\n");
        return 1;
    }

    memset(frame, 255, frame_size);

    struct timespec start, now;
    clock_gettime(CLOCK_MONOTONIC, &start);

    /*
    Duration of simulation in seconds.
    The loop will simulate streaming for 5 seconds.
    */
    int duration_seconds = 5;

    while (1)
    {
        memcpy(buffer, frame, frame_size);

        /*
        Control frame rate.
        Sleep for 1/fps seconds.
        Example:
        30 fps -> sleep ~33ms per frame.
        */
        usleep(1000000 / fps);   

        clock_gettime(CLOCK_MONOTONIC, &now);

        double elapsed =
            (now.tv_sec - start.tv_sec) +
            (now.tv_nsec - start.tv_nsec) / 1e9;

        if (elapsed >= duration_seconds)
            break;
    }

    clock_gettime(CLOCK_MONOTONIC, &now);

    double total_time =
        (now.tv_sec - start.tv_sec) +
        (now.tv_nsec - start.tv_nsec) / 1e9;

    printf("Execution time: %.3f seconds\n", total_time);

    free(frame);
    free(buffer);

    return 0;
}
