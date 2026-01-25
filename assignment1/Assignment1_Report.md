# EEP 522 – Assignment 1: System Configuration

**Author:** Yu-An Chen  
**Course:** EEP 522 – Embedded And Real Time Systems  
**Platform:** Raspberry Pi 4 Model B (1GB)  
**Date:** January 25, 2026  

---

## Abstract

This assignment documents the configuration of a Raspberry Pi 4 Model B as a headless embedded development platform.  
The objective was to install and configure the operating system, establish remote communication, enable cross-development from a host machine, and execute a performance experiment.  

Unlike a traditional setup, most initialization steps were completed during the Raspberry Pi Imager installation phase, which significantly reduced manual configuration.  
The system was successfully configured using SSH-based access, Visual Studio Code Remote SSH for development, and GitHub for version control.  

An experimental workload was executed and visualized using gnuplot. During execution, a hardware revision mismatch was identified and corrected in the source code to support the target board.
---

## 1. Introduction

Embedded systems development requires a stable, reproducible, and well-documented hardware and software environment.  
The purpose of this assignment is to configure a Raspberry Pi as a headless embedded Linux platform suitable for development, experimentation, and performance evaluation.

This configuration serves as the foundation for subsequent assignments. Emphasis was placed on minimizing manual setup, leveraging modern tooling, and documenting all challenges encountered during system bring-up.
---

## 2. Hardware and Software Setup

### 2.1 Hardware

- Raspberry Pi 4 Model B (1GB RAM)
- microSD card (32GB)
- Power supply compatible with Raspberry Pi 4
- WiFi network connection
- Host machine running Windows

### 2.2 Software

- Raspberry Pi OS 32-bit
- OpenSSH
- GNU Compiler Collection (gcc)
- Visual Studio Code (Remote SSH)
- Git and GitHub
- Gnuplot

---

## 3. Operating System Installation

Raspberry Pi OS (32-bit) was installed using the Raspberry Pi Imager tool.  
During the imaging process, the following configurations were completed:

- Username and password creation
- WiFi network configuration
- SSH enabled
- Hostname set
- Locale and keyboard layout set to English (US)

As a result, many steps described in the assignment handout (manual WiFi setup, hostname change, SSH installation) were already completed before first boot.

After installation, the system was verified using:

```
yuanchen_eep522@rpi4-eep522:~ $ uname -a

Linux rpi4-eep522 6.12.47+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.12.47-1+rpt1 (2025-09-16) aarch64 GNU/Linux
```

Although the OS installed was 32-bit, the kernel reported an aarch64 architecture. This behavior is expected on Raspberry Pi 4, where a 64-bit kernel may be used with a 32-bit userland.

---

## 4. Headless System Configuration

To configure the Raspberry Pi as a headless embedded system:

- The graphical desktop environment was disabled.
- Console auto-login was enabled using `sudo raspi-config`.
- SSH access was enabled to allow remote login.
- System packages were updated and upgraded after reboot.

After reboot, the system booted directly into a terminal without requiring a display, keyboard, or mouse.

System updates were performed using the following commands:
```
sudo apt update
sudo apt upgrade
```
These steps ensured that all installed packages were up to date before further configuration and experimentation.

Remote access was verified using SSH:

` ssh yuanchen_eep522@rpi4-eep522.local `

---

## 5. Communication and Development Environment

### 5.1 SSH Communication

Secure Shell (SSH) was used as the primary communication mechanism between the host machine and the Raspberry Pi.  
This enabled remote login, file transfer, and command execution.

### 5.2 Cross-Development Environment

A cross-development workflow was established using:

- SSH for remote access
- gcc for native compilation on the Raspberry Pi
- Visual Studio Code with the Remote SSH extension

This setup allowed editing, compiling, and executing code directly on the Raspberry Pi from the host machine.

A simple “Hello World” program was compiled and executed successfully to verify the toolchain.
```
yuanchen_eep522@rpi4-eep522:~/eep522/assignment1 $ gcc hellow.c -o hellow
yuanchen_eep522@rpi4-eep522:~/eep522/assignment1 $ ./hellow
hello_world
```

---

## 6. Experiment Execution

### 6.1 Experiment Setup


The provided experiment archive (`A1_source.zip`) was transferred to the Raspberry Pi and organized under the following structure:
```
eep522/
└── assignment1/
└── experiment/
```

Commands used:
```
scp A1_source.zip yuanchen_eep522@rpi4-eep522.local:~/eep522/assignment1/
cd ~/eep522/assignment1
mkdir experiment
mv A1_source.zip experiment/
cd experiment
unzip A1_source.zip
```
Gnuplot was installed using:
```
sudo apt install gnuplot
```
---

### 6.2 Initial Failure and Root Cause Analysis

The experiment was executed using:

`./run.sh`


However, the generated plots were empty.  
Inspection of the program output revealed the following error:

`-- E: model type unknown a03115`

This indicated that the Raspberry Pi 4 Model B (1GB) revision code (`a03115`) was not recognized by the program.

---




### 6.3 Code Modification

To resolve this issue, the model translation logic in `prototype.c` was updated.

Original logic only supported revision `a03111`.  
Although a03111 and a03115 are distinct hardware revision codes, both correspond to Raspberry Pi 4 Model B with identical memory configuration and CPU architecture. Since the experiment only depends on memory size and access behavior, both revisions can be safely mapped to the same internal model representation.
The following modification was applied:
```
if (!strcmp(model,"a03111") || !strcmp(model,"a03115"))
{
    g_core.model = 0xa03115;
    g_core.memory_size_gb = 1;
    g_core.revision = 1.1;
    return;
}
```

This change allows the program to correctly identify both revision codes as Raspberry Pi 4 Model B (1GB).  
Since both revisions share the same memory configuration, treating them equivalently is valid and resolves the execution failure.

After recompilation, the experiment completed successfully and produced valid data and plots.

---

## 7. Results

The experiment generated multiple plots illustrating:

- Execution time trends
- Cache-friendly vs cache-unfriendly memory access patterns
- Temperature variation relative to baseline

The results confirm that the system was operating correctly and that the workload executed as expected.
| ![tests](images/plot_tests.jpg) | ![memsys](images/plot_memsys.jpg) | ![memlib](images/plot_memlib.jpg) |
| :---: | :---: | :---: |
| plot_tests.jpg | plot_memsys.jpg | plot_memlib.jpg |


---

## 8. Discussion

Several challenges were encountered during this assignment:

- Incorrect user creation during initial setup
- Confusion regarding 32-bit OS versus 64-bit kernel reporting
- Unsupported hardware revision code in the provided experiment
- Empty output plots due to early program termination

Each issue was resolved through systematic debugging, documentation review, and source code inspection.  
This process reinforced the importance of understanding system initialization details and hardware identifiers in embedded Linux environments.

---

## 9. Safe Shutdown Procedure

To prevent filesystem corruption, the system was always shut down using the following command before power removal:

`sudo halt`

This ensured that all filesystem buffers were flushed and the system entered a safe state prior to disconnecting power.

---

## 10. Version Control

All coursework files were managed using Git and stored in a private GitHub repository.  
Version control was used to prevent data loss and to track incremental changes throughout system configuration and experimentation.

---

## 9. Conclusion

This assignment successfully established a complete and reproducible embedded development environment on a Raspberry Pi 4 Model B operating in headless mode.  
By leveraging Raspberry Pi Imager for initial configuration, many traditionally manual steps—such as WiFi setup, SSH enablement, and hostname configuration—were completed prior to first boot, significantly simplifying system bring-up.

Remote development was enabled using SSH and Visual Studio Code, allowing source code editing, compilation, and execution without requiring direct physical access to the board.  
A cross-development workflow was validated through successful compilation and execution of test programs and experimental workloads.

During experimentation, an unsupported hardware revision code was identified and resolved through a careful analysis of hardware equivalence and software abstraction.  
By mapping functionally identical Raspberry Pi revisions to a common internal representation, the experiment was able to execute correctly and generate meaningful performance data.

All configuration steps, debugging decisions, and commands were documented to ensure reproducibility and long-term maintainability.  
The resulting system provides a stable foundation for subsequent assignments involving embedded software development, performance analysis, and system-level experimentation.


---

## 11. References

1. Raspberry Pi OS – Updating and Upgrading Software  
   https://www.raspberrypi.com/documentation/computers/os.html#update-software  
   (Reference for using `sudo apt update` and `sudo apt upgrade` on Raspberry Pi OS)

2. Raspberry Pi OS – Headless Setup and SSH Configuration  
   https://www.raspberrypi.com/documentation/computers/remote-access.html  
   (Reference for enabling SSH and remote access without a monitor)

4. Secure Shell (SSH) – Protocol and Usage  
   https://www.openssh.com/manual.html  
   (Reference for SSH-based remote login and secure communication)

6. Gnuplot – Official Documentation  
   http://www.gnuplot.info/documentation.html  
   (Reference for generating plots from experiment data)
8. Raspberry Pi Hardware Revision Codes  
   https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#raspberry-pi-revision-codes  
   (Used as a reference to understand Raspberry Pi revision code formats and memory configurations. The specific revision code `a03115` was not explicitly listed; however, comparison with documented Raspberry Pi 4 Model B 1GB revisions (e.g., `a03111`) indicated equivalent hardware characteristics, justifying equivalent handling in the experiment source code.)
9. OpenAI ChatGPT  
   (Used as an auxiliary tool to assist with command lookup, debugging error messages,
   and clarifying system configuration steps. All technical actions were verified
   through official documentation and direct system observation.)

---

## 12. Appendices

### Appendix A: User Correction and Auto-Login Adjustment (Technical Record)

During initial setup, an incorrect username was created and configured for console auto-login.  
This prevented the old user account from being terminated, as it was automatically logged in at boot.

To resolve this issue, the following steps were performed:

1. A new user account was created and granted sudo privileges.
2. Console auto-login was reconfigured using `raspi-config` to use the new account.
3. The system was rebooted to ensure the old user was no longer active.
4. Remaining processes owned by the old user were terminated.
5. The old user account was safely removed.

Key commands used:
```
sudo adduser yuanchen_eep522
sudo usermod -aG sudo yuanchen_eep522
sudo raspi-config
sudo pkill -u yuanchen_eep520
sudo userdel -r yuanchen_eep520
```

This ensured that the system used the correct course-related username and avoided permission conflicts.

--- 

### Appendix B: Project Directory Structure
```
eep522/
└── assignment1/
├── Assignment1_Report.md
├── hellow.c
├── experiment/
└── images/
```