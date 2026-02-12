## CPU and Memory Bandwidth Characterization

### Objective

The objective of this experiment was to evaluate how image resolution and frame rate affect CPU utilization and memory bandwidth on the Raspberry Pi platform. The experiment simulates a camera workload by copying frame-sized memory buffers at a controlled frame rate.

This exploration aims to understand whether the system is compute-bound or memory-bound when processing image-like data streams.

---

### Experimental Setup

A C program was developed to simulate camera frame processing. The program:

- Allocates two frame-sized memory buffers
- Copies one buffer into another using `memcpy`
- Controls execution rate using `usleep()` to simulate FPS
- Runs for a fixed duration of 5 seconds
- Measures execution time using `clock_gettime()`
- CPU utilization measured using the Linux `time` utility

Frame size calculation:

- RGB888 format (3 bytes per pixel)
- Frame size = width × height × 3

Test configurations:

| Resolution | FPS | Frame Size |
|------------|-----|------------|
| 1280 × 720 | 15  | 2.64 MB |
| 1920 × 1080 | 30 | 5.93 MB |

---

### Results

#### 720p @ 15 FPS

## CPU and Memory Bandwidth Characterization

### Objective

The objective of this experiment was to evaluate how image resolution and frame rate affect CPU utilization and memory bandwidth on the Raspberry Pi platform. The experiment simulates a camera workload by copying frame-sized memory buffers at a controlled frame rate.

This exploration aims to understand whether the system is compute-bound or memory-bound when processing image-like data streams.

---

### Experimental Setup

A C program was developed to simulate camera frame processing. The program:

- Allocates two frame-sized memory buffers
- Copies one buffer into another using `memcpy`
- Controls execution rate using `usleep()` to simulate FPS
- Runs for a fixed duration of 5 seconds
- Measures execution time using `clock_gettime()`
- CPU utilization measured using the Linux `time` utility

Frame size calculation:

- RGB888 format (3 bytes per pixel)
- Frame size = width × height × 3

Test configurations:

| Resolution | FPS | Frame Size |
|------------|-----|------------|
| 1280 × 720 | 15  | 2.64 MB |
| 1920 × 1080 | 30 | 5.93 MB |

---

### Results

#### 720p @ 15 FPS
```
real ≈ 5.05 s
user ≈ 0.109 s
sys ≈ 0.004 s
```
Estimated CPU utilization:

CPU ≈ (user + sys) / real  
CPU ≈ (0.109 + 0.004) / 5.05 ≈ 2.2%

Theoretical memory traffic:

2.64 MB × 15 FPS ≈ 39.6 MB/s

---

#### 1080p @ 30 FPS
```
real ≈ 5.03 s
user ≈ 0.369 s
sys ≈ 0.025 s
```
Estimated CPU utilization:

CPU ≈ (0.369 + 0.025) / 5.03 ≈ 7.8%

Theoretical memory traffic:

5.93 MB × 30 FPS ≈ 177.9 MB/s

---

### Analysis

The experimental results show approximately a 4× increase in CPU utilization when increasing both resolution and frame rate.

This aligns with the theoretical scaling of memory traffic:

- Resolution increase ≈ 2.2×
- FPS increase ≈ 2×
- Total memory traffic ≈ 4.4×

The measured CPU increase closely matches the expected increase in memory bandwidth demand.

This indicates that the workload is primarily **memory-bandwidth bound**, rather than compute-bound.

---

### Observations

- CPU utilization remains relatively low (<10%) even at 1080p @ 30 FPS.
- The Raspberry Pi platform has significant headroom for additional processing.
- Frame processing workload scales approximately linearly with memory traffic.
- System behavior appears deterministic under controlled frame rates.

---

### Insight

In image-processing workloads, memory bandwidth can become the dominant bottleneck rather than arithmetic computation. Resolution and frame rate directly affect memory traffic, which in turn determines CPU utilization.

This experiment provides a baseline understanding of system capacity before introducing additional processing such as image analysis or multithreading.

---



![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)




## Real-Time Behavior and Scheduling Analysis

### Objective

The objective of this experiment was to evaluate the timing determinism of periodic task execution on a Raspberry Pi running Linux. Specifically, the experiment aimed to measure:

- Frame interval stability (jitter)
- Context switch behavior
- The impact of CPU load on scheduling determinism

This helps characterize whether the platform behaves as a deterministic real-time system or as a soft real-time system under load.

---

### Methodology

A periodic task was implemented in C to simulate a 30 FPS workload. The program:

- Uses `usleep()` to wake up every 33.333 ms
- Measures actual elapsed time between wakeups using `clock_gettime()`
- Computes jitter as the difference between actual and target intervals
- Reports:
  - Maximum jitter
  - Minimum jitter
  - Average jitter
  - Voluntary and non-voluntary context switches from `/proc/self/status`

The test was executed for 5 seconds under two conditions:

1. Idle system (no additional load)
2. High CPU load using `yes > /dev/null`

---

### Results

#### Case 1: Idle System

```
Target interval: 0.033333 s
Max jitter: 0.000568 s
Min jitter: 0.000061 s
Avg jitter: 0.000078 s

voluntary_ctxt_switches: 152
nonvoluntary_ctxt_switches: 0
```

Observations:

- Voluntary context switches closely matched the expected sleep cycles (≈150 for 30 FPS × 5 s).
- No non-voluntary context switches occurred.
- Maximum jitter remained below 0.6 ms.
- CPU usage observed in `top` was low.

---

#### Case 2: High CPU Load (`yes > /dev/null`)

```
Target interval: 0.033333 s
Max jitter: 0.003879 s
Min jitter: 0.000061 s
Avg jitter: 0.000119 s

voluntary_ctxt_switches: 150
nonvoluntary_ctxt_switches: 4
```


Observations:

- Voluntary context switches remained consistent with expected sleep cycles.
- Non-voluntary context switches increased (4 occurrences).
- Maximum jitter increased significantly (≈3.9 ms).
- `top` indicated high CPU utilization due to the additional load process.

---

### Analysis

The results clearly demonstrate the impact of system load on scheduling determinism.

Under idle conditions:

- The periodic task executed with minimal jitter.
- No forced preemption occurred.
- The system behaved in a relatively deterministic manner.

Under high CPU load:

- Non-voluntary context switches were observed.
- Maximum jitter increased by approximately 7×.
- Scheduling interference from competing processes introduced measurable timing variability.

This confirms that Linux on Raspberry Pi behaves as a **soft real-time system**. While timing stability is acceptable under low load, deterministic guarantees cannot be maintained under CPU contention.

---

### Context Switch Interpretation

- `voluntary_ctxt_switches` correspond to explicit `usleep()` calls.
- `nonvoluntary_ctxt_switches` indicate scheduler preemption.
- The increase in non-voluntary switches under load directly correlates with increased jitter.

---

### Conclusion

This experiment demonstrates that:

- Periodic tasks on Linux exhibit low jitter under idle conditions.
- CPU load increases scheduler interference.
- Non-voluntary context switches are a measurable indicator of preemption.
- Timing determinism degrades under contention.

Therefore, the Raspberry Pi running standard Linux should be considered a **soft real-time platform**, suitable for latency-tolerant embedded workloads but not for hard real-time guarantees.

Figures from `top` illustrating CPU utilization under both conditions are included for reference.


## Multithreading: Race Condition and Mutex Synchronization

### Objective

The purpose of this experiment was to investigate race conditions in a multi-threaded environment and evaluate whether mutex synchronization eliminates non-deterministic behavior. Additionally, the impact of compiler optimization on observable race behavior was examined.

---

### Experimental Design

A shared global counter was incremented concurrently by two threads:

```
int counter = 0;

void* increment(void* arg)
{
    for (int i = 0; i < ITERATIONS; i++)
    {
        counter++;   // Not atomic
    }
    return NULL;
}
```
Two versions were tested:

Without mutex protection

With mutex protection

The expected final result was:

```
Expected = number_of_threads × ITERATIONS
```
The program was compiled using both -O0 and -O2 optimization levels.


### Results

#### Case 1: No Mutex, Compiled with `-O0`

```
Final counter = 10135379
Expected = 40000000
```

The final counter value was significantly lower than expected.  
Each execution produced different incorrect values.

This demonstrates a classic race condition.

---

#### Case 2: With Mutex, Compiled with `-O0`

```
Final counter = 40000000
Expected = 40000000
```

The result was consistently correct across all executions.

Mutex synchronization successfully eliminated concurrent memory corruption.

---

### Why the Race Occurs

The operation:

```
counter++
```

is not atomic. It consists of three steps:

1. Load `counter` from memory  
2. Add 1  
3. Store back to memory  

If two threads execute these steps simultaneously, the following can occur:

```
Thread A loads 10
Thread B loads 10
Thread A stores 11
Thread B stores 11
```

One increment is lost.

This results in a non-deterministic final counter value.

---

### Impact of Compiler Optimization

When compiled with `-O2`, the race condition sometimes appeared less frequently or did not immediately produce incorrect results.

However, this does not eliminate the race condition.

Compiler optimization changes instruction scheduling, register usage, and memory access patterns, which may reduce the probability of interleaving. The underlying data race remains present because the shared variable is not protected.

Race conditions represent undefined behavior and may manifest differently depending on:

- Optimization level  
- Scheduling  
- CPU architecture  
- System load  

Correctness must not rely on compiler behavior.

---

### Conclusion

This experiment demonstrates:

- Unsynchronized shared memory access leads to non-deterministic results.
- Race conditions may not always produce visible errors.
- Compiler optimization can change the probability of observable race behavior.
- Mutex synchronization guarantees correctness by enforcing mutual exclusion.

This confirms that multi-threaded embedded applications must use proper synchronization mechanisms to ensure data integrity, regardless of apparent behavior under certain build configurations.


# Multithreaded Camera Pipeline Simulation  
## Producer–Consumer Without vs With Mutex

### Objective

The purpose of this experiment is to demonstrate the impact of synchronization mechanisms in a multithreaded producer–consumer pipeline running on a Raspberry Pi 4 multicore system. The simulation models a simplified camera pipeline where:

- A **camera thread** produces frames.
- A **processing thread** consumes frames.
- A shared circular buffer is used for inter-thread communication.

Two versions were implemented:
1. Without mutex protection
2. With mutex protection

The system was compiled using `-O0` and executed on a Raspberry Pi 4 (quad-core ARM Cortex-A72).

---

### Observations

#### 1️⃣ Version Without Mutex

The non-synchronized version exhibited the following behaviors:

- Frame IDs were skipped inconsistently (e.g., Frame 10, 13, 16 missing).
- The buffer count appeared valid most of the time but was subject to race conditions.
- Frame overwriting occurred when both threads accessed shared variables concurrently.
- Execution behavior was nondeterministic across runs.

Although the program did not crash, the absence of mutual exclusion allowed simultaneous access to shared variables (`count`, `in`, `out`), leading to data corruption and frame loss.

This demonstrates a classic race condition caused by non-atomic updates to shared state in a multicore environment.

---

#### 2️⃣ Version With Mutex

The mutex-protected version showed:

- Deterministic and stable behavior.
- No buffer corruption.
- Consistent buffer count values.
- No double-processing of frames.
- Frame skipping only occurred due to buffer-full conditions, not race conditions.

By protecting the critical section with `pthread_mutex_lock()` and `pthread_mutex_unlock()`, shared data modifications became atomic and thread-safe.

---

### Analysis

In the non-synchronized implementation, the following sequence may occur:

- Thread A reads `count`
- Thread B reads `count`
- Thread A modifies and writes `count`
- Thread B modifies and overwrites `count`

This leads to lost updates and inconsistent buffer states.

Since Raspberry Pi 4 runs on multiple cores, threads execute truly in parallel, increasing the likelihood of concurrent access conflicts.

The mutex ensures:

- Mutual exclusion
- Serialized access to shared memory
- Data integrity across cores
- Deterministic system behavior

---

### Conclusion

This experiment demonstrates that:

- Multithreaded programs accessing shared memory without synchronization are vulnerable to race conditions.
- Even if a system does not crash, silent data corruption may occur.
- Proper synchronization using mutex is essential in real-time camera or vision pipelines.
- In practical embedded vision systems, failure to protect shared buffers may lead to frame corruption, incorrect processing results, and unreliable system behavior.

Therefore, synchronization primitives are mandatory when implementing producer–consumer architectures on multicore embedded systems.


# System Characterization – Raspberry Pi 4 Model B

## 1. Operating System and Kernel

Command used:

    uname -a

Result:

    Linux 6.12.47+rpt-rpi-v8 #1 SMP PREEMPT Debian aarch64 GNU/Linux

### Analysis

- Architecture: 64-bit ARM (aarch64)
- Kernel: Linux 6.12.x
- SMP enabled (Symmetric Multiprocessing)
- PREEMPT enabled (low-latency preemption model)

The PREEMPT kernel suggests improved scheduling responsiveness compared to non-preemptible kernels, but this is not a hard real-time configuration (PREEMPT_RT is not confirmed).

---

## 2. CPU Architecture

Commands used:

    cat /proc/cpuinfo
    lscpu

### Summary

- Model: Raspberry Pi 4 Model B Rev 1.5
- SoC: Broadcom BCM2711
- CPU: ARM Cortex-A72
- Cores: 4
- Threads per core: 1
- CPU Max Frequency: 1.8 GHz
- CPU Min Frequency: 600 MHz
- Architecture: ARMv8-A (64-bit)

### Observations

- True multicore execution is supported.
- No hyperthreading.
- Dynamic frequency scaling (600–1800 MHz) may affect determinism.
- Suitable for parallel workloads such as camera pipelines or producer-consumer models.

---

## 3. Cache Hierarchy

From `lscpu`:

- L1 Data Cache: 128 KiB total (32 KiB per core × 4)
- L1 Instruction Cache: 192 KiB total (48 KiB per core × 4)
- L2 Cache: 1 MiB shared

### Analysis

The cache hierarchy is critical for:

- Memory throughput
- Context switching performance
- Real-time responsiveness
- Multithreaded workloads

The shared 1 MiB L2 cache introduces potential cache contention between cores during parallel processing (e.g., producer-consumer workloads).

---

## 4. Memory Configuration

Command used:

    free -h

Result:

- Total RAM: ~906 MiB usable
- Swap: 905 MiB
- Available Memory: ~564 MiB

### Observations

- Approximately 1 GB RAM model
- Swap enabled (may introduce nondeterministic latency)
- RAM type: LPDDR4 (per hardware documentation)

### Embedded System Concern

Using swap in embedded real-time applications is undesirable because:

- It introduces unpredictable latency
- It affects determinism
- It may cause performance jitter under memory pressure

For production systems, swap should likely be disabled.

---

## 5. CPU Features

From `/proc/cpuinfo`:

    Features: fp asimd evtstrm crc32 cpuid

### Interpretation

- fp → hardware floating-point support
- asimd → Advanced SIMD (NEON)
- crc32 → hardware CRC support

This indicates:

- Suitable for image processing
- Capable of SIMD acceleration
- Suitable for signal processing tasks

---

## 6. Security & Vulnerabilities

The board shows:

- Spectre v1 mitigated
- Spectre v2 vulnerable
- Speculative store bypass vulnerable

While this is not critical for prototyping, it may affect:

- Performance
- Security requirements in production deployments

---

## 7. Determinism Considerations

The following characteristics may impact real-time determinism:

1. Linux general-purpose kernel
2. CPU frequency scaling
3. Swap memory enabled
4. Shared L2 cache
5. Non-RT scheduler

Conclusion:

The Raspberry Pi 4 is capable of moderate real-time responsiveness but is not a hard real-time platform without kernel modification (e.g., PREEMPT_RT).

---

## 8. Suitability for Multithreaded Camera Pipeline

Given:

- 4 physical cores
- SIMD support
- 1 MiB shared L2 cache
- 1 GB RAM

The board is suitable for:

- Experimental real-time image processing
- Multithreaded producer-consumer architectures
- Lightweight AI inference

Limitations:

- Not deterministic under heavy load
- Thermal throttling may occur
- Shared cache contention possible


1st time

yuanchen_eep522@rpi4-eep522:~/eep522/assignment2 $ systemd-analyze
Startup finished in 3.145s (kernel) + 19.054s (userspace) = 22.200s 
graphical.target reached after 18.497s in userspace.
yuanchen_eep522@rpi4-eep522:~/eep522/assignment2 $ systemd-analyze blame
6.860s NetworkManager.service
5.963s NetworkManager-wait-online.service
2.759s cloud-init-main.service
1.149s dev-mmcblk0p2.device
 976ms e2scrub_reap.service
 854ms udisks2.service
 747ms user@1001.service
 683ms rpi-eeprom-update.service
 664ms ModemManager.service
 543ms accounts-daemon.service
 450ms polkit.service
 442ms cloud-init-local.service
 426ms systemd-fsck@dev-disk-by\x2dpartuuid-ceaf83be\x2d01.service
 422ms avahi-daemon.service
 417ms bluetooth.service
 415ms rpi-resize-swap-file.service
 366ms cloud-init-network.service
 351ms dbus.service
 351ms systemd-udev-trigger.service
 292ms keyboard-setup.service
 283ms systemd-udevd.service
 280ms rp1-test.service
 280ms glamor-test.service
 275ms wpa_supplicant.service
 271ms systemd-journald.service
 247ms systemd-binfmt.service
 236ms cloud-final.service
 220ms ssh.service
 212ms rpi-setup-loop@var-swap.service
 203ms cups.service
 203ms systemd-zram-setup@zram0.service
 202ms systemd-logind.service
 192ms cloud-config.service

2nd time
yuanchen_eep522@rpi4-eep522:~/eep522 $ systemd-analyze
Startup finished in 3.023s (kernel) + 18.890s (userspace) = 21.914s 
graphical.target reached after 18.386s in userspace.
yuanchen_eep522@rpi4-eep522:~/eep522 $ systemd-analyze blame
6.744s NetworkManager.service
6.344s apt-daily-upgrade.service
5.962s NetworkManager-wait-online.service
2.712s cloud-init-main.service
1.249s dev-mmcblk0p2.device
1.128s e2scrub_reap.service
 857ms udisks2.service
 721ms user@1001.service
 712ms rpi-eeprom-update.service
 667ms ModemManager.service
 556ms accounts-daemon.service
 451ms polkit.service
 433ms cloud-init-local.service
 432ms avahi-daemon.service
 428ms bluetooth.service
 383ms systemd-binfmt.service
 381ms cloud-init-network.service
 372ms systemd-udev-trigger.service
 363ms dbus.service
 355ms rpi-resize-swap-file.service
 313ms systemd-fsck@dev-disk-by\x2dpartuuid-ceaf83be\x2d01.service
 304ms rp1-test.service
 283ms keyboard-setup.service
 281ms glamor-test.service
 279ms systemd-journald.service
 269ms wpa_supplicant.service
 246ms cloud-final.service
 241ms systemd-udevd.service
 223ms systemd-logind.service
 199ms proc-sys-fs-binfmt_misc.mount
 198ms cloud-config.service
 191ms plymouth-start.service
 185ms systemd-hostnamed.service

 3rd time
 yuanchen_eep522@rpi4-eep522:~/eep522 $ systemd-analyze
Startup finished in 3.339s (kernel) + 19.090s (userspace) = 22.430s 
graphical.target reached after 18.572s in userspace.
yuanchen_eep522@rpi4-eep522:~/eep522 $ systemd-analyze blame
6.911s NetworkManager.service
5.962s NetworkManager-wait-online.service
2.758s cloud-init-main.service
1.169s dev-mmcblk0p2.device
 949ms e2scrub_reap.service
 893ms udisks2.service
 687ms rpi-eeprom-update.service
 629ms user@1001.service
 629ms ModemManager.service
 567ms accounts-daemon.service
 467ms polkit.service
 431ms cloud-init-local.service
 420ms avahi-daemon.service
 413ms bluetooth.service
 403ms keyboard-setup.service
 375ms cloud-init-network.service
lines 1-16


yuanchen_eep522@rpi4-eep522:~/eep522/assignment2 $ gcc memory_copy_test.c -O0 -o memtest
yuanchen_eep522@rpi4-eep522:~/eep522/assignment2 $ ./memtest
Size: 1024 bytes | Time: 0.000002 s | Bandwidth: 405.72 MB/s
Size: 1048576 bytes | Time: 0.001326 s | Bandwidth: 754.17 MB/s
Size: 104857600 bytes | Time: 0.137362 s | Bandwidth: 728.00 MB/s