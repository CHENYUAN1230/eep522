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

pthread_mutex_t mutex;

/* -------- Camera Thread -------- */
void* camera_thread(void* arg) {
    for (int i = 0; i < MAX_FRAMES; i++) {

        Frame frame;
        frame.frame_id = i;

        pthread_mutex_lock(&mutex);

        if (count < BUFFER_SIZE) {
            buffer[in] = frame;
            in = (in + 1) % BUFFER_SIZE;
            count++;

            printf("[Camera] Frame %d captured (count=%d)\n",
                   frame.frame_id, count);
        }

        pthread_mutex_unlock(&mutex);
        usleep(10000);
    }
    return NULL;
}

/* -------- Processor Thread -------- */
void* processing_thread(void* arg) {
    for (int i = 0; i < MAX_FRAMES; i++) {

        pthread_mutex_lock(&mutex);

        if (count > 0) {
            Frame frame = buffer[out];
            out = (out + 1) % BUFFER_SIZE;
            count--;

            printf("   [Processor] Frame %d processed (count=%d)\n",
                   frame.frame_id, count);
        }

        pthread_mutex_unlock(&mutex);
        usleep(15000);
    }
    return NULL;
}

int main() {

    pthread_t cam, proc;

    pthread_mutex_init(&mutex, NULL);

    pthread_create(&cam, NULL, camera_thread, NULL);
    pthread_create(&proc, NULL, processing_thread, NULL);

    pthread_join(cam, NULL);
    pthread_join(proc, NULL);

    pthread_mutex_destroy(&mutex);

    return 0;
}
