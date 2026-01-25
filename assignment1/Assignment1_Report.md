# EEP 522 – Assignment 1: System Configuration

**Author:** Yu-An Chen  
**Course:** EEP 522 – Embedded And Real Time Systems  
**Platform:** Raspberry Pi 4 Model B (1GB)  
**Date:** January 25, 2026  

---

## Abstract

This assignment documents the configuration of a Raspberry Pi 4 Model B as a headless embedded development platform.  
The objective was to install and configure the operating system, establish remote communication, enable cross-development from a host machine, and execute a performance experiment.  
The system was successfully configured using Raspberry Pi OS with SSH-based access.  
Development and debugging were performed remotely using Visual Studio Code, and version control was implemented using GitHub.  
An experimental workload was executed and visualized using gnuplot to verify correct system operation.

---

## 1. Introduction

Embedded systems development requires a stable and reproducible hardware and software environment.  
The purpose of this assignment is to configure a Raspberry Pi as a headless embedded Linux platform suitable for development and experimentation.

This configuration serves as the foundation for subsequent assignments, which rely on reliable communication, compilation, execution, and performance measurement capabilities.  
Emphasis was placed on remote access, system robustness, and reproducibility.

---

## 2. Hardware and Software Setup

### 2.1 Hardware

- Raspberry Pi 4 Model B (1GB RAM)
- microSD card (≥16GB)
- Power supply compatible with Raspberry Pi 4
- Ethernet / WiFi network connection
- Host machine running Windows

### 2.2 Software

- Raspberry Pi OS 32-bit (Bullseye)
- OpenSSH
- GNU Compiler Collection (gcc)
- Visual Studio Code (Remote SSH)
- Git and GitHub
- Gnuplot

---

## 3. Operating System Installation

Raspberry Pi OS (32-bit, Bullseye) was installed using the Raspberry Pi Imager tool.  
During installation, the system language was set to English (US) and the keyboard layout to US.

After installation, the system was verified using:

uname -a


The operating system booted successfully and entered a Linux environment.

---

## 4. Headless System Configuration

To configure the Raspberry Pi as a headless embedded system:

- The graphical desktop environment was disabled.
- Console auto-login was enabled using raspi-config.
- SSH access was enabled to allow remote login.

After reboot, the system booted directly into a terminal without requiring a display, keyboard, or mouse.

Remote access was verified using SSH:

ssh yuanchen_eep522@rpi4-eep522.local


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

---

## 6. Experiment Execution

### 6.1 Experiment Setup

The experiment source code was transferred to the Raspberry Pi and organized under a dedicated directory structure:


eep522/
└── assignment1/
└── experiment/


The experiment measures memory performance, matrix computation behavior, and temperature changes under load.

### 6.2 Code Modification

During execution, the program reported an unknown model error due to an unsupported Raspberry Pi revision code (a03115).  
The source file prototype.c was modified to correctly recognize the Raspberry Pi 4 Model B (1GB).

This modification allowed the experiment to execute successfully.

### 6.3 Execution and Visualization

The experiment was executed using:

./run.sh


The script generated data files and visualized results using gnuplot.  
Graphs illustrating execution time, memory access behavior, and temperature variation were produced.

---

## 7. Results

The experiment completed successfully and produced the following observations:

- Execution time increased with workload size as expected.
- Cache-friendly memory access patterns demonstrated improved performance.
- Temperature increased gradually during sustained computation but remained within safe operating limits.

Generated graphs provide visual confirmation of correct system operation.

---

## 8. Discussion

Several challenges were encountered during configuration:

- Incorrect model identification due to missing revision code support.
- Initial confusion regarding 32-bit OS versus 64-bit kernel reporting.
- Organization of files and experiment outputs.

These issues were resolved through system inspection, code modification, and structured project organization.  
The debugging process reinforced the importance of understanding hardware identifiers and Linux system files.

---

## 9. Conclusion

This assignment successfully established a complete embedded development environment on a Raspberry Pi 4 Model B.  
The system was configured to operate in headless mode, support remote development, and execute performance experiments.

The resulting platform is stable, reproducible, and suitable for future assignments involving embedded software development and performance analysis.

---

## 10. Version Control

All coursework files were managed using Git and stored in a private GitHub repository.  
Version control was used to prevent data loss and track incremental changes during system configuration and experimentation.

---

## 11. References

1. Raspberry Pi Documentation – https://www.raspberrypi.com/documentation/
2. Debian GNU/Linux – https://www.debian.org/
3. Secure Shell (SSH) – https://en.wikipedia.org/wiki/Secure_Shell
4. GNU Compiler Collection – https://gcc.gnu.org/
5. Gnuplot Documentation – http://www.gnuplot.info/
6. GitHub Documentation – https://docs.github.com/

---

## 12. Appendices

### Appendix A: Useful Linux Commands

- uname -a  
- ls -lh  
- df -h  
- du -chs  
- ssh  
- scp  
- git status  

### Appendix B: Project Directory Structure

eep522/
└── assignment1/
├── Assignment1_Report.md
├── hellow.c
├── experiment/
└── screenshots/