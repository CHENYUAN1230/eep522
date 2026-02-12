#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define BUFFER_SIZE 3
#define MAX_FRAMES 50

typedef struct {
    int frame_id;
} Frame;

Frame buffer[BUFFER_SIZE];
int count = 0;
int in = 0;
int out = 0;

/* -------- Camera Thread -------- */
void* camera_thread(void* arg) {
    for (int i = 0; i < MAX_FRAMES; i++) {

        Frame frame;
        frame.frame_id = i;

        // ❌ No protection
        if (count < BUFFER_SIZE) {
            buffer[in] = frame;
            in = (in + 1) % BUFFER_SIZE;
            count++;

            printf("[Camera] Frame %d captured (count=%d)\n",
                   frame.frame_id, count);
        }

        usleep(10000);
    }
    return NULL;
}

/* -------- Processor Thread -------- */
void* processing_thread(void* arg) {
    for (int i = 0; i < MAX_FRAMES; i++) {

        // ❌ No protection
        if (count > 0) {
            Frame frame = buffer[out];
            out = (out + 1) % BUFFER_SIZE;
            count--;

            printf("[Processor] Frame %d processed (count=%d)\n",
                   frame.frame_id, count);
        }

        usleep(15000);
    }
    return NULL;
}

int main() {

    pthread_t cam, proc;

    pthread_create(&cam, NULL, camera_thread, NULL);
    pthread_create(&proc, NULL, processing_thread, NULL);

    pthread_join(cam, NULL);
    pthread_join(proc, NULL);

    return 0;
}
