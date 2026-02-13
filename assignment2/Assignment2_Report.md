# Assignment 2 – Exploration  
## Raspberry Pi 4 System Characterization Report  

Author: Yu-An Chen  

C Proficiency Level: Intermediate    
Coding Standard Used: C99  
Estimated Time Spent: ~24 hours  
GitHub Repository (Source Code):
https://github.com/CHENYUAN1230/eep522/tree/main/assignment2

# 1. Objective

The following characterization questions were defined to evaluate the Raspberry Pi 4 as an embedded soft real-time platform:

1. What CPU architecture and cache hierarchy does the board use?
2. What is the effective memory bandwidth across cache and DRAM scales?
3. How deterministic is periodic task scheduling under Linux?
4. What is the impact of CPU load on scheduling jitter?
5. How reliable is multithreaded shared memory access without synchronization?
6. What GPIO control mechanisms are available and how deterministic are they?
7. What is the boot time and startup variability?
8. Is the platform suitable for limited or mass production?
9. Is the system appropriate for soft or hard real-time workloads?



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



# 2. System Overview

## 2.1 Operating System and Kernel

### Command used:


```
uname -a
```

### Result:
```
Linux rpi4-eep522 6.12.47+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.12.47-1+rpt1 (2025-09-16) aarch64 GNU/Linux
```

### Analysis

- Architecture: ARMv8-A (64-bit)
- Kernel: Linux 6.12.47
- SMP enabled (4 cores)
- PREEMPT enabled (low-latency kernel, not PREEMPT_RT)

The system uses a general-purpose Linux kernel with preemption enabled. This improves responsiveness but does not guarantee hard real-time behavior.


## 2.2 CPU Architecture

### Commands used:

```
cat /proc/cpuinfo
lscpu
```

### Summary:

- Model: Raspberry Pi 4 Model B Rev 1.5
- SoC: Broadcom BCM2711
- CPU: ARM Cortex-A72
- Cores: 4
- Threads per core: 1
- CPU max frequency: 1.8 GHz
- CPU min frequency: 600 MHz

### Cache hierarchy:

- L1 Data Cache: 32 KB per core (128 KB total)
- L1 Instruction Cache: 48 KB per core (192 KB total)
- L2 Cache: 1 MB shared

### Observations

- True multicore execution supported
- Shared L2 cache may introduce contention
- Dynamic frequency scaling may affect determinism


# 3. CPU and Memory Bandwidth Characterization

## 3.1 Objective

To evaluate how image resolution and frame rate affect CPU utilization and memory bandwidth when simulating a camera workload.

The goal is to determine whether the Raspberry Pi 4 becomes compute-bound or memory-bandwidth bound under increasing image-processing demand.

---

## 3.2 Methodology

A C program was implemented to simulate a camera frame-processing workload.

The program:

- Allocates two frame-sized buffers
- Uses `memcpy()` to simulate frame transfer
- Uses `usleep()` to control frame rate
- Runs for 5 seconds
- Measures execution time using `clock_gettime()`
- Measures CPU usage using the Linux `time` command

Frame format:

- RGB888 (3 bytes per pixel)

Test configurations:

| Resolution | FPS | Frame Size |
|------------|-----|------------|
| 1280×720   | 15  | 2.64 MB    |
| 1920×1080  | 30  | 5.93 MB    |

---

## 3.3 Commands

Compilation:

```bash
gcc frame_test.c -O0 -o frame_test
```

Test 1 – 720p @ 15 FPS:

```bash
time ./frame_test 1280 720 15
```

Test 2 – 1080p @ 30 FPS:

```bash
time ./frame_test 1920 1080 30
```

---

## 3.4 Results

### 720p @ 15 FPS

```
Resolution: 1280x720
FPS: 15
Frame size: 2.64 MB
Execution time: 5.016 seconds

real    5.039 s
user    0.144 s
sys     0.024 s
```

CPU utilization:

```
(0.144 + 0.024) / 5.039 ≈ 3.3%
```

Theoretical memory traffic:

```
2.64 MB × 15 ≈ 39.6 MB/s
```

---

### 1080p @ 30 FPS

```
Resolution: 1920x1080
FPS: 30
Frame size: 5.93 MB
Execution time: 5.026 seconds

real    5.043 s
user    0.488 s
sys     0.013 s
```

CPU utilization:

```
(0.488 + 0.013) / 5.043 ≈ 9.9%
```

Theoretical memory traffic:

```
5.93 MB × 30 ≈ 177.9 MB/s
```

---

## 3.5 Analysis

Resolution increased by ≈ 2.2×  
Frame rate increased by ≈ 2×  

Expected memory traffic increase:

```
2.2 × 2 ≈ 4.4×
```

Measured CPU increase:

```
3.3% → 9.9%  ≈ 3× increase
```

Observations:

- Wall-clock time remains constant (~5 s) due to fixed test duration.
- CPU utilization increases proportionally with memory traffic.
- System time (`sys`) remains minimal, indicating low kernel overhead.
- The majority of CPU time is spent in user-space `memcpy()`.

Even at 1080p @ 30 FPS:

- CPU utilization remains under 10%.
- No compute saturation is observed.
- Significant processing headroom remains.

Interpretation:

The workload scales primarily with memory transfer size and frame rate.

The Raspberry Pi 4 does not become compute-bound under these conditions.  
Instead, performance behavior is more consistent with a memory-bandwidth-dominated workload.

Given the measured utilization, the platform can likely support additional processing stages (e.g., filtering, compression, or lightweight inference) without immediate CPU bottleneck.


# 4. Memory Hierarchy Benchmark

## 4.1 Objective

To evaluate cache hierarchy behavior and effective memory bandwidth across different working-set sizes.

The goal is to observe how performance changes when data fits within L1 cache, L2 cache, and DRAM.

---

## 4.2 Methodology

A memory copy benchmark was implemented using `memcpy()`.

The program:

- Allocates buffers of varying sizes
- Measures copy time using high-resolution timing
- Computes effective bandwidth (MB/s)
- Repeats measurements to reduce timing noise

Test sizes were selected to approximate:

- L1 cache capacity
- L2 cache capacity
- DRAM-scale working set

---

## 4.3 Commands

Compilation:

```bash
gcc memory_copy_test.c -O0 -o memory_copy_test
```

Execution:

```bash
./memory_copy_test
```

---

## 4.4 Results

```
Size: 1024 bytes       | Time: 0.000002 s | Bandwidth: 405.72 MB/s
Size: 1048576 bytes    | Time: 0.001326 s | Bandwidth: 754.17 MB/s
Size: 104857600 bytes  | Time: 0.137362 s | Bandwidth: 728.00 MB/s
```

---

## 4.5 Analysis

### 1 KB (L1 Cache Region)

- 1 KB is significantly smaller than L1 data cache (32 KB per core).
- Data remains entirely within L1.
- Observed bandwidth: ~406 MB/s.

At this scale, latency dominates more than throughput due to extremely small transfer size.

---

### 1 MB (L2 Cache Region)

- 1 MB approximates the shared L2 cache size.
- Data likely resides within L2 during transfer.
- Observed bandwidth: ~754 MB/s.

Bandwidth increases significantly compared to 1 KB due to improved streaming efficiency and better utilization of memory pipeline.

---

### 100 MB (DRAM Region)

- 100 MB greatly exceeds total cache capacity.
- Data must be transferred from main memory (LPDDR4 DRAM).
- Observed bandwidth: ~728 MB/s.

The relatively small drop from L2-level bandwidth indicates:

- Efficient DRAM subsystem
- Effective cache line prefetching
- Optimized `memcpy()` implementation

---

### Performance Trends

- Bandwidth increases from 1 KB to 1 MB due to improved pipeline efficiency.
- DRAM bandwidth remains close to L2 bandwidth.
- No dramatic bandwidth collapse observed when exceeding cache.

This suggests:

- Strong memory controller performance
- Effective hardware prefetching
- Good cache-line streaming behavior

---

## 4.6 Interpretation

The Raspberry Pi 4 demonstrates stable and high memory bandwidth across working-set scales.

For image-processing workloads:

- Moderate-resolution frames (several MB) will primarily operate at DRAM bandwidth levels.
- Observed DRAM bandwidth (~700+ MB/s) is sufficient for typical camera pipelines below ~200 MB/s demand.

The system exhibits strong memory subsystem performance suitable for moderate embedded image-processing applications.



# 5. Real-Time Behavior and Scheduling Analysis

## 5.1 Objective

To evaluate the timing determinism of a periodic task running on a Raspberry Pi 4 under standard Linux.

Specifically, this experiment measures:

- Periodic execution stability (jitter)
- Context switch behavior
- Impact of CPU contention on scheduling
- Whether the system behaves as hard or soft real-time

---

## 5.2 Methodology

A 30 FPS periodic task was implemented in `jitter_test.c`.

Target interval:

```
1 / 30 FPS ≈ 0.033333 seconds
```

The program:

- Uses `usleep(33333)` for periodic wakeups
- Uses `clock_gettime(CLOCK_MONOTONIC)` for precise timing
- Computes jitter:

```
jitter = |actual_interval − target_interval|
```

- Reads context switch statistics from `/proc/self/status`:
  - voluntary_ctxt_switches
  - nonvoluntary_ctxt_switches

Each experiment ran for 5 seconds under two conditions:

1. Idle system
2. High CPU load

---

## 5.3 Commands

Compilation:

```bash
gcc jitter_test.c -O0 -o jitter_test
```

Idle test:

```bash
./jitter_test
```

Load generation:

```bash
yes > /dev/null &
./jitter_test
killall yes
```

---

## 5.4 Results

### Idle System

```
Target interval: 0.033333 s
Max jitter: 0.000568 s
Min jitter: 0.000061 s
Avg jitter: 0.000078 s

voluntary_ctxt_switches: 152
nonvoluntary_ctxt_switches: 0
```

Expected wakeups:

```
30 FPS × 5 s ≈ 150
```

Measured voluntary context switches closely match expected sleep cycles.

![jitter_test](images/jitter_test_idle.png)
---

### High CPU Load

```
Target interval: 0.033333 s
Max jitter: 0.003879 s
Min jitter: 0.000061 s
Avg jitter: 0.000119 s

voluntary_ctxt_switches: 150
nonvoluntary_ctxt_switches: 4
```

Worst-case jitter increase:

```
0.003879 / 0.000568 ≈ 6.8×
```

≈ 7× increase under load.

![jitter_test_highLoad](images/jitter_test_highLoad.png)

---

## 5.5 Analysis

### Idle Condition

- No non-voluntary context switches occurred.
- Jitter remained below 0.6 ms.
- Average jitter ≈ 78 µs.
- Scheduling interference minimal.

This indicates relatively stable periodic behavior when system load is low.

---

### Under CPU Load

- 4 non-voluntary (forced) context switches occurred.
- Worst-case jitter increased to ~3.9 ms.
- Average jitter increased moderately.
- CPU contention introduced measurable scheduling interference.

The correlation between forced preemption and increased jitter is clear.

---

### Scheduler Interpretation

Raspberry Pi runs standard Linux with the Completely Fair Scheduler (CFS).

CFS characteristics:

- Time-sharing scheduler
- No fixed execution deadlines
- Ensures fairness, not determinism

Under load:

- Competing runnable tasks increase preemption probability
- Time slice expiration causes forced context switches
- Latency variability increases

Cache coherence and SMP execution do not prevent scheduling-induced jitter.

---

### Real-Time Classification

Hard real-time systems require:

- Strict upper bound on latency
- No unbounded jitter
- Deterministic scheduling guarantees

Observed behavior:

- Jitter increases under load
- Forced preemption occurs
- Worst-case latency is not bounded

Therefore:

The Raspberry Pi 4 running standard Linux behaves as a **soft real-time system**.

It is suitable for latency-tolerant workloads (camera pipelines, UI, logging), but not for hard real-time control systems.

Achieving hard real-time behavior would require:

- PREEMPT_RT kernel
- Real-time scheduling policies (e.g., SCHED_FIFO)
- Or a dedicated RTOS


# 6. GPIO Pin Control and Hardware Interaction

## 6.1 Objective

To evaluate GPIO control capabilities on the Raspberry Pi 4 using the modern Linux `libgpiod` interface.

This experiment investigates:

- Determinism of GPIO access
- Linux GPIO resource ownership model
- Suitability of libgpiod for embedded systems
- Basic I/O latency characteristics

---

## 6.2 Methodology

The experiment was implemented in `led_test.c`.

### Hardware Setup

- LED connected to GPIO 17 (output)
- Push-button connected to GPIO 27 (input)
- Internal pull-up resistor enabled

### Software Behavior

The program:

- Opens `/dev/gpiochip0`
- Requests exclusive access to GPIO lines
- Configures:
  - GPIO 17 as output
  - GPIO 27 as input with pull-up bias
- Polls button state every 10 ms
- Turns LED ON when button is pressed

Polling interval:

```
usleep(10000)  // 10 ms
```

---

## 6.3 Commands

Compilation:

```bash
gcc led_test.c -o led_test -lgpiod
```

Execution:

```bash
./led_test
```

---

## 6.4 Results

Observed behavior:

- LED toggled correctly in response to button press.
- GPIO line requests were exclusive (no simultaneous access allowed).
- Pull-up bias maintained stable HIGH state when button unpressed.
- CPU utilization remained below 1%.
- Response delay approximately equal to polling interval (~10 ms).

![led_test_demo](images/led_test_demo.png)
---

## 6.5 Analysis

### Resource Management

The `libgpiod` interface uses the Linux GPIO character device model:

- GPIO lines accessed via `/dev/gpiochipX`
- Exclusive ownership enforced by the kernel
- Prevents multiple processes from driving the same line

This ensures safe hardware access in multi-process systems.

---

### Latency Characteristics

Because the implementation uses polling:

```
usleep(10000)
```

Worst-case latency:

```
≈ 10 ms
```

Actual latency depends on:

- Scheduler timing
- CPU load
- Context switches

Under high system load, polling wakeups may be delayed slightly, increasing response variability.

---

### Determinism Evaluation

The experiment demonstrates:

- Functional and stable GPIO control
- Deterministic behavior limited by polling interval
- Scheduling jitter affects response timing

The system does not provide interrupt-level determinism in polling mode.

An interrupt-driven implementation using edge detection would reduce latency and improve responsiveness.

---

### Embedded Suitability

Advantages:

- Clean and modern API
- Kernel-managed exclusive access
- Support for pull-up/down bias configuration
- Low CPU overhead

Limitations:

- Subject to Linux scheduling jitter
- Polling introduces inherent latency
- Not suitable for hard real-time interrupt control without PREEMPT_RT

---

The Raspberry Pi 4 using `libgpiod` provides reliable GPIO control suitable for:

- Prototyping
- Low-frequency digital I/O
- Educational and moderate embedded applications

However, deterministic interrupt-driven systems would require:

- PREEMPT_RT kernel
- Real-time scheduling policies
- Or bare-metal firmware



# 7. Multithreading and Synchronization

## 7.1 Objective

To evaluate race conditions and synchronization behavior on a multicore Raspberry Pi 4 system.

This experiment investigates:

- Effects of unsynchronized shared memory access
- Impact of thread count on race severity
- Correctness guarantees provided by mutex
- Behavior of producer–consumer pipelines without synchronization

---

## 7.2 Methodology

Four programs were tested:

1. `multithread_test.c`  
   - 4 threads  
   - Shared global counter  
   - No mutex protection  

2. `multithread_mutex_test.c`  
   - 4 threads  
   - Shared global counter  
   - Mutex-protected critical section  

3. `camera_multithread_sim.c`  
   - 2 threads (producer–consumer)  
   - Shared circular buffer  
   - No mutex protection  

4. `camera_multithread_mutex_sim.c`  
   - 2 threads (producer–consumer)  
   - Shared circular buffer  
   - Mutex-protected critical section  

The experiments were compiled with `-O0` to clearly expose race behavior.

---

## 7.3 Commands

### 4-Thread Counter (No Mutex)

```bash
gcc -O0 multithread_test.c -o multithread_test -lpthread
./multithread_test
```

### 4-Thread Counter (With Mutex)

```bash
gcc -O0 multithread_mutex_test.c -o multithread_mutex_test -lpthread
./multithread_mutex_test
```

### Camera Pipeline (No Mutex)

```bash
gcc -O0 camera_multithread_sim.c -o camera_multithread_sim -lpthread
./camera_multithread_sim
```

### Camera Pipeline (With Mutex)

```bash
gcc -O0 camera_multithread_mutex_sim.c -o camera_multithread_mutex_sim -lpthread
./camera_multithread_mutex_sim
```

---

## 7.4 Results

### 4-Thread Counter – No Mutex

Expected:

```
4 × ITERATIONS = 40000000
```

Observed:

```
Final counter = 10135379
Expected      = 40000000
```

Behavior:

- Final value significantly below expected
- Each run produces different incorrect results
- Severe nondeterministic behavior

---

### 4-Thread Counter – With Mutex

```
Final counter = 40000000
Expected      = 40000000
```

Behavior:

- Deterministic across runs
- No lost updates
- Correct final result

---

### 2-Thread Camera Pipeline – No Mutex

Observed behavior:

- Frame IDs skipped (e.g., 10, 13, 16 missing)
- Occasional frame overwriting
- Inconsistent buffer count
- Nondeterministic execution
- No crash, but silent data corruption

---

### 2-Thread Camera Pipeline – With Mutex

Observed behavior:

- Deterministic execution
- No frame corruption
- No double processing
- Consistent buffer state
- Frame drop only when buffer full (expected condition)

---

## 7.5 Analysis

### Why the Race Occurs

The operation:

```
counter++
```

is not atomic. It expands to:

1. Load
2. Increment
3. Store

Possible interleaving with 4 threads:

```
Thread A loads 10
Thread B loads 10
Thread C loads 10
Thread D loads 10
Thread A stores 11
Thread B stores 11
Thread C stores 11
Thread D stores 11
```

Multiple increments are lost.

---

### 4-Thread Counter Behavior

- High concurrency pressure
- Multiple cores executing in parallel
- Severe race amplification
- Large deviation from expected value

Race severity increases with thread count.

---

### 2-Thread Producer–Consumer Behavior

Even with only two threads:

- Shared variables (`count`, `in`, `out`) modified concurrently
- Lost updates occur
- Logical data corruption appears

Race conditions do not require many threads.  
Two concurrent threads are sufficient.

---

### Cache Coherence vs Atomicity

Raspberry Pi 4:

- Quad-core ARM Cortex-A72
- Shared memory architecture
- Cache-coherent SMP system

Important distinction:

- Cache coherence ensures memory visibility
- It does NOT ensure atomicity

Correctness requires explicit synchronization.

---

### Effect of Mutex

Mutex guarantees:

- Mutual exclusion
- Serialized access to shared memory
- Deterministic behavior
- Correct program semantics

The cost of mutex is minor compared to correctness benefits.

---

The experiments demonstrate that:

- Unsynchronized shared memory leads to nondeterministic behavior.
- Race severity increases with concurrency.
- Even 2-thread pipelines require synchronization.
- Multicore embedded systems must use proper synchronization primitives.

For embedded camera or vision systems, failure to protect shared buffers can lead to:

- Frame corruption
- Data loss
- Unreliable processing
- Difficult-to-debug nondeterministic behavior



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



# 9. Determinism and System Limitations

Factors affecting determinism:

- General-purpose Linux scheduler
- Shared L2 cache
- Dynamic frequency scaling
- Swap enabled
- SD card storage latency

Conclusion:

The Raspberry Pi 4 is suitable for soft real-time workloads but not safety-critical deterministic systems.



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

# 11. Impact of Modern Tooling on Embedded Systems

- PREEMPT_RT improving determinism
- libgpiod replacing legacy sysfs
- Rust gaining traction in embedded Linux
- Advanced profiling tools enabling deeper system characterization

# 12. Conclusion

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

# 13. References

[1] Raspberry Pi Ltd., "Raspberry Pi 4 Model B Documentation"  
https://www.raspberrypi.com/documentation/computers/raspberry-pi.html

[2] Broadcom Inc., "BCM2711 ARM Peripherals (Raspberry Pi 4 SoC Documentation)"  
https://datasheets.raspberrypi.com/bcm2711/bcm2711-peripherals.pdf

[3] ARM Ltd., "ARM Cortex-A72 Technical Reference Manual"  
https://developer.arm.com/documentation/100095/latest/

[4] Linux Kernel Documentation, "Completely Fair Scheduler (CFS)"  
https://www.kernel.org/doc/html/latest/scheduler/sched-design-CFS.html

[5] Linux Manual Pages:
   - clock_gettime(2): https://man7.org/linux/man-pages/man2/clock_gettime.2.html  
   - pthread(7): https://man7.org/linux/man-pages/man7/pthreads.7.html  
   - sched(7): https://man7.org/linux/man-pages/man7/sched.7.html  

[6] libgpiod Documentation 
https://libgpiod.readthedocs.io/en/latest/

[7] systemd Documentation, "systemd-analyze"  
https://www.freedesktop.org/software/systemd/man/systemd-analyze.html

[8] Raspberry Pi Ltd., "GPIO Character Device Interface (libgpiod & modern GPIO subsystem)"  
https://www.raspberrypi.com/documentation/computers/os.html#gpio-character-device-interface

[9] ChatGPT used as an auxiliary tool for:
   - Clarifying Linux scheduler concepts (CFS vs real-time scheduling)
   - Verifying theoretical explanations of race conditions and memory hierarchy behavior
   - Reviewing technical writing clarity, structure and translation