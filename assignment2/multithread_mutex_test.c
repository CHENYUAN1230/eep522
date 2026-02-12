#include <stdio.h>
#include <pthread.h>

#define ITERATIONS 10000000

int counter = 0;
pthread_mutex_t lock;

void* increment(void* arg)
{
    for (int i = 0; i < ITERATIONS; i++)
    {
        pthread_mutex_lock(&lock);
        counter++;
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}

int main()
{
    pthread_t t1, t2, t3, t4;

    pthread_mutex_init(&lock, NULL);

    pthread_create(&t1, NULL, increment, NULL);
    pthread_create(&t2, NULL, increment, NULL);
    pthread_create(&t3, NULL, increment, NULL);
    pthread_create(&t4, NULL, increment, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    pthread_join(t3, NULL);
    pthread_join(t4, NULL);

    printf("Final counter = %d\n", counter);
    printf("Expected = %d\n", 4 * ITERATIONS);

    pthread_mutex_destroy(&lock);

    return 0;
}
