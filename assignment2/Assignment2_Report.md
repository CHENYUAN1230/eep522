# Assignment 2 – Exploration  
## Raspberry Pi 4 System Characterization Report  

Author: Yu-An Chen  
C Proficiency Level: Beginner  
Coding Standard Used: C99  

---

# 1. Objective

The objective of this assignment is to characterize the Raspberry Pi 4 Model B platform and establish a theoretical and experimental baseline of its hardware and software capabilities.

The focus areas selected for this exploration include:

- CPU architecture and cache hierarchy  
- Memory bandwidth behavior and working-set scaling  
- GPIO peripheral control and pin configuration using libgpiod  
- Real-time scheduling characteristics and jitter analysis  
- Multithreading behavior and synchronization mechanisms  
- Boot time analysis and startup determinism  
- Suitability for limited (~1000 units) and mass production (>10,000 units)  

These areas were selected to evaluate whether the Raspberry Pi 4 platform is suitable for embedded image-processing workloads and moderate real-time applications. The exploration emphasizes memory hierarchy behavior, scheduling determinism, peripheral control capability, and multicore synchronization characteristics.


---

# 2. System Overview

## 2.1 Operating System and Kernel

Command used:


```
uname -a
```

Result:
```
Linux rpi4-eep522 6.12.47+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.12.47-1+rpt1 (2025-09-16) aarch64 GNU/Linux
```

### Analysis

- Architecture: ARMv8-A (64-bit)
- Kernel: Linux 6.12.47
- SMP enabled (4 cores)
- PREEMPT enabled (low-latency kernel, not PREEMPT_RT)

The system uses a general-purpose Linux kernel with preemption enabled. This improves responsiveness but does not guarantee hard real-time behavior.

---

## 2.2 CPU Architecture

Commands used:

```
cat /proc/cpuinfo
lscpu
```

Summary:

- Model: Raspberry Pi 4 Model B Rev 1.5
- SoC: Broadcom BCM2711
- CPU: ARM Cortex-A72
- Cores: 4
- Threads per core: 1
- CPU max frequency: 1.8 GHz
- CPU min frequency: 600 MHz

Cache hierarchy:

- L1 Data Cache: 32 KB per core (128 KB total)
- L1 Instruction Cache: 48 KB per core (192 KB total)
- L2 Cache: 1 MB shared

### Observations

- True multicore execution supported
- Shared L2 cache may introduce contention
- Dynamic frequency scaling may affect determinism

---

# 3. CPU and Memory Bandwidth Characterization

## 3.1 Objective

To evaluate how image resolution and frame rate affect CPU utilization and memory bandwidth when simulating a camera workload.

The experiment determines whether the system is compute-bound or memory-bandwidth bound.

---

## 3.2 Experimental Setup

A C program simulated frame processing:

- Two frame-sized buffers allocated
- `memcpy()` used to simulate frame transfer
- `usleep()` controlled FPS
- Duration: 5 seconds
- CPU measured via `time`
- Execution time measured using `clock_gettime()`

Frame format:

- RGB888 (3 bytes per pixel)

Test configurations:

| Resolution | FPS | Frame Size |
|------------|-----|------------|
| 1280×720   | 15  | 2.64 MB    |
| 1920×1080  | 30  | 5.93 MB    |

---

## 3.3 Results

### Test Command - 720p @ 15 FPS


```
time ./frame_test 1280 720 15
```

Output:
```
Resolution: 1280x720
FPS: 15
Frame size: 2.64 MB
Execution time: 5.016 seconds

real    0m5.039s
user    0m0.144s
sys     0m0.024s
```

CPU utilization:

```
CPU ≈ (0.144 + 0.024) / 5.039
CPU ≈ 0.168 / 5.039 ≈ 3.3%

```

Theoretical memory traffic:

```
2.64 MB × 15 FPS ≈ 39.6 MB/s
```

---

### Test Command - 1080p @ 30 FPS

```
time ./frame_test 1920 1080 30
```

Output:
```
Resolution: 1920x1080
FPS: 30
Frame size: 5.93 MB
Execution time: 5.026 seconds

real    0m5.043s
user    0m0.488s
sys     0m0.013s
```

CPU utilization:

```
CPU ≈ (0.488 + 0.013) / 5.043
CPU ≈ 0.501 / 5.043 ≈ 9.9%

```

Theoretical memory traffic:

```
5.93 MB × 30 FPS ≈ 177.9 MB/s
```

---

## 3.4 Analysis

Resolution increase ≈ 2.2×
FPS increase ≈ 2×
Expected memory traffic increase ≈ 4.4×

Measured CPU increase:
```
3.3% → 9.9%
≈ 3× increase
```

Observations:

- Real time remains constant (~5 seconds) due to fixed test duration.
- CPU utilization increases proportionally with memory traffic.
- Even at 1080p @ 30 FPS, CPU usage remains under 10%.
- System time remains very small, indicating minimal kernel overhead.
- Majority of CPU time is spent in user-space memcpy().

Conclusion:

The workload scales primarily with memory transfer size and frame rate.

The system is not compute-bound.

Given the linear scaling of CPU usage with memory traffic and low overall utilization, the workload is more indicative of a memory-bandwidth dominated workload, though the Raspberry Pi 4 still has significant headroom for additional processing.

---

# 4. Memory Hierarchy Benchmark

To evaluate cache behavior, a memory copy benchmark was executed.

Command:

```
gcc memory_copy_test.c -O0 -o memtest
./memtest
```

Results:

```
Size: 1024 bytes     | Time: 0.000002 s | Bandwidth: 405.72 MB/s
Size: 1048576 bytes  | Time: 0.001326 s | Bandwidth: 754.17 MB/s
Size: 104857600 bytes| Time: 0.137362 s | Bandwidth: 728.00 MB/s
```

### Interpretation

- 1 KB fits entirely within L1 cache (32 KB per core)
- 1 MB approximates L2 cache size (1 MB shared)
- 100 MB exceeds cache → DRAM access

Observation:

Bandwidth remains relatively high, indicating efficient memory subsystem performance. Slight variations may be due to cache line behavior and memcpy optimization.

Conclusion:

The system exhibits strong memory bandwidth capability suitable for moderate image-processing workloads.

---

# 5. Real-Time Behavior and Scheduling Analysis

## 5.1 Objective

To measure periodic timing jitter and scheduling interference under load.

---

## 5.2 Methodology

- 30 FPS periodic task using `usleep(33333)`
- Measured jitter with `clock_gettime()`
- Measured context switches from `/proc/self/status`
- Tested under idle and high CPU load

---

## 5.3 Results

### Idle System

```
Max jitter: 0.000568 s
Avg jitter: 0.000078 s
voluntary switches: 152
nonvoluntary switches: 0
```

### High CPU Load

```
Max jitter: 0.003879 s
Avg jitter: 0.000119 s
voluntary switches: 150
nonvoluntary switches: 4
```

---

## 5.4 Analysis

Under load:

- Jitter increased ~7×
- Non-voluntary context switches observed
- Scheduler interference measurable

Conclusion:

The Raspberry Pi running standard Linux behaves as a **soft real-time system**, not hard real-time.

---

# 6. GPIO Pin Control and Hardware Interaction

## 6.1 Objective

The objective of this experiment was to evaluate GPIO control capabilities on the Raspberry Pi 4 using the modern Linux `libgpiod` interface.

This experiment aims to determine:

- Whether GPIO access is deterministic
- How Linux manages GPIO resource ownership
- The suitability of libgpiod for embedded applications
- Basic I/O latency characteristics

---

## 6.2 Library Selection

The experiment used:

libgpiod (GPIO character device interface)

Reasons for selection:

- Replaces deprecated sysfs GPIO interface
- Official Linux-supported interface
- Uses `/dev/gpiochipX`
- Provides structured configuration APIs
- Supports bias configuration, edge detection, and exclusive access

---

## 6.3 Experimental Setup

Hardware:

- LED connected to GPIO 17
- Push-button connected to GPIO 27
- Internal pull-up resistor enabled

Software:

The program:

- Opens `/dev/gpiochip0`
- Configures GPIO 17 as output
- Configures GPIO 27 as input with pull-up bias
- Requests exclusive line access
- Polls button state every 10 ms
- Turns LED ON when button pressed


Compilation:

```
gcc gpio_test.c -o gpio_test -lgpiod
```

---

## 6.4 Observations

- Exclusive access prevents multiple processes from using the same GPIO line.
- Pull-up bias ensures stable logic HIGH when button is not pressed.
- Polling interval (10 ms) determines responsiveness.
- CPU usage negligible (<1%).
- Response delay approximately equal to polling interval.

---

## 6.5 Determinism and Latency Analysis

Because the program uses polling with `usleep(10000)`:

- Worst-case latency ≈ 10 ms
- Actual latency depends on scheduler timing
- Under CPU load, delay variability may increase

This confirms:

- GPIO control via libgpiod is functional
- Deterministic response is limited by Linux scheduling
- Interrupt-based edge detection would improve latency

---

## 6.6 Suitability for Embedded Systems

Advantages:

- Clean structured API
- Safe exclusive resource handling
- Kernel-managed GPIO control
- Supports pull-up/down configuration

Limitations:

- Subject to Linux scheduling jitter
- Polling introduces latency
- Not suitable for hard real-time interrupt control without PREEMPT_RT

---

## 6.7 Conclusion

The Raspberry Pi 4 using libgpiod provides reliable GPIO control suitable for:

- Prototyping
- Low-frequency digital I/O
- Educational embedded systems

However, for deterministic interrupt-driven systems, additional real-time kernel support or bare-metal approaches would be required.



# 7. Multithreading and Synchronization

## 7.1 Race Condition Test

Without mutex:

```
Final counter = 10135379
Expected      = 40000000
```

With mutex:

```
Final counter = 40000000
Expected      = 40000000
```

Conclusion:

- `counter++` is not atomic
- Race conditions cause lost updates
- Mutex guarantees correctness

---

## 7.2 Producer–Consumer Camera Simulation

Two versions tested:

1. Without mutex → frame corruption and nondeterministic behavior  
2. With mutex → stable deterministic behavior  

Conclusion:

Multicore systems require synchronization to maintain data integrity.

---

# 8. Boot Time Characterization

Command:

```
systemd-analyze
```

Results:

Run 1:

```
Startup finished in 3.145s (kernel) + 19.054s (userspace) = 22.200s
```

Run 2:

```
Startup finished in 3.023s (kernel) + 18.890s (userspace) = 21.914s
```

Run 3:

```
Startup finished in 3.339s (kernel) + 19.090s (userspace) = 22.430s
```

### Observations

- Kernel time stable (~3.1 s)
- Userspace time variable (~18–19 s)
- Total boot ≈ 22 s
- Not deterministic

Conclusion:

The platform is unsuitable for applications requiring deterministic startup timing.

---

# 9. Determinism and System Limitations

Factors affecting determinism:

- General-purpose Linux scheduler
- Shared L2 cache
- Dynamic frequency scaling
- Swap enabled
- SD card storage latency

Conclusion:

The Raspberry Pi 4 is suitable for soft real-time workloads but not safety-critical deterministic systems.

---

# 10. Production Considerations

## Limited Production (~1000 units)

- Acceptable for prototyping
- SD card reliability must be evaluated
- Thermal design required
- Disable swap for real-time use

## Mass Production (>10,000 units)

Limitations:

- 22 s nondeterministic boot time
- Consumer-grade SD storage
- Linux scheduling nondeterminism
- Potential thermal throttling

Recommendation:

- Consider eMMC storage
- Use PREEMPT_RT or RTOS
- Consider custom embedded board

---

# 11. Conclusion

The Raspberry Pi 4 Model B provides:

- 4-core ARM Cortex-A72
- 1 MB shared L2 cache
- Strong memory bandwidth
- SIMD support
- Soft real-time scheduling

The platform is well-suited for:

- Experimental camera pipelines
- Multithreaded processing
- Educational embedded systems

However, it is not suitable for:

- Hard real-time guarantees
- Deterministic startup systems
- Safety-critical embedded devices

Overall, the Raspberry Pi 4 serves as a capable soft real-time embedded platform for prototyping and moderate-scale deployment.

---
