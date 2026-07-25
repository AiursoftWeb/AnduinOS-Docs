# Running ARM64 AnduinOS in QEMU on AMD64

This guide covers running the ARM64 edition of AnduinOS on an AMD64 (x86_64) host using QEMU with TCG emulation. This is useful for testing ARM64 builds without dedicated ARM hardware.

Before starting, we need to understand the following concepts:

* **TCG emulation**: Since the host CPU is AMD64 and the guest is ARM64, KVM acceleration is **not available**. QEMU falls back to pure software emulation (TCG), which is significantly slower than native speed.
* **`virt` machine type**: The standard ARM64 virtual machine in QEMU. It uses PCIe for devices and does **not** emulate IDE controllers — all storage must use `virtio-scsi` or `virtio-blk`.
* **AAVMF firmware**: The ARM Architecture Virtual Machine Firmware (AAVMF) is the ARM64 build of EDK2/TianoCore UEFI. It provides UEFI boot support for ARM64 guests.
* **VirtIO SCSI**: A paravirtualized SCSI controller that provides better performance than emulated IDE and is the standard storage interface for the `virt` machine.
* **GOP driver**: The Graphics Output Protocol driver. Some builds of AAVMF do not include a GOP driver, meaning the firmware can only output to the serial console, not to a graphical display.

!!! warning "EDK2 2025.11 LPA2 bug"

    Using `-cpu max` with Debian/Ubuntu's AAVMF firmware (edk2 2025.11) causes the firmware to hang after printing the version banner. This is due to an LPA2 (52-bit addressing) incompatibility in the MMU initialization. The workaround is to use a specific CPU model like `neoverse-n1` instead of `-cpu max`.

    See [Debian Bug #1124749](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1124749) and [tianocore/edk2 Issue #11962](https://github.com/tianocore/edk2/issues/11962) for details.

## Installing QEMU for ARM64

To install QEMU and the ARM64 UEFI firmware on AnduinOS, run the following command:

```bash title="Install QEMU ARM64 packages"
sudo apt install qemu-system-arm qemu-efi-aarch64
```

Download the ARM64 ISO image from the [AnduinOS releases page](https://github.com/Aiursoft/AnduinOS/releases).

## Prepare the firmware variables

The writable UEFI variables file must be copied from the system template before starting the VM:

```bash title="Copy UEFI variables template"
cp /usr/share/AAVMF/AAVMF_VARS.fd ./vars.fd
```

## Booting the installer

To boot the AnduinOS ARM64 ISO, run the following command:

```bash title="Start ARM64 VM with graphical display"
qemu-system-aarch64 \
    -M virt,gic-version=3 \
    -cpu neoverse-n1 \
    -m 8192 \
    -smp 8 \
    -drive if=pflash,file=/usr/share/AAVMF/AAVMF_CODE.fd,format=raw,readonly=on \
    -drive if=pflash,file=./vars.fd,format=raw \
    -device virtio-scsi-pci,id=scsihw0 \
    -drive file=./AnduinOS-2.0.1-arm64.iso,if=none,id=cdrom,format=raw,readonly=on \
    -device scsi-cd,bus=scsihw0.0,drive=cdrom,bootindex=100 \
    -netdev user,id=net0 \
    -device virtio-net-pci,netdev=net0 \
    -device virtio-gpu \
    -device qemu-xhci \
    -device usb-tablet \
    -device usb-kbd \
    -display gtk
```

Here is a breakdown of each parameter:

| Parameter | Purpose |
|---|---|
| `-M virt,gic-version=3` | ARM `virt` machine type with GICv3 interrupt controller |
| `-cpu neoverse-n1` | ARM Neoverse-N1 CPU model (avoids the EDK2 2025.11 LPA2 bug) |
| `-m 8192` | 8 GB of RAM |
| `-smp 8` | 8 CPU cores |
| `-drive if=pflash,...` | UEFI firmware code (read-only) and variable store (writable) |
| `virtio-scsi-pci` | Paravirtualized SCSI controller (the `virt` machine has no IDE) |
| `scsi-cd,bootindex=100` | Attach the ISO as a SCSI CD-ROM device with boot priority |
| `virtio-net-pci` | Paravirtualized network adapter |
| `virtio-gpu` | Paravirtualized GPU |
| `qemu-xhci` | USB 3.0 controller for input devices |
| `usb-tablet,usb-kbd` | USB input devices for mouse cursor and keyboard |
| `-display gtk` | Open a GTK window for the VM display |

## Connecting to the virtual machine

After running the command, a GTK window will open showing the VM display. Click inside the window to capture keyboard and mouse input. Press `Ctrl+Alt+G` to release the input back to the host.

The UEFI firmware will show a boot menu. Select the SCSI CD-ROM device to boot from the ISO. You should then see the AnduinOS installer.

!!! tip "Serial console fallback"

    If the graphical display shows "Guest has not initialized the display", the AAVMF build may not include a GOP driver. In this case, fall back to serial-only mode by replacing `-display gtk` with `-nographic`:

    ```bash title="Start ARM64 VM with serial console"
    qemu-system-aarch64 \
        -M virt,gic-version=3 \
        -cpu neoverse-n1 \
        -m 8192 \
        -smp 8 \
        -drive if=pflash,file=/usr/share/AAVMF/AAVMF_CODE.fd,format=raw,readonly=on \
        -drive if=pflash,file=./vars.fd,format=raw \
        -device virtio-scsi-pci,id=scsihw0 \
        -drive file=./AnduinOS-2.0.1-arm64.iso,if=none,id=cdrom,format=raw,readonly=on \
        -device scsi-cd,bus=scsihw0.0,drive=cdrom,bootindex=100 \
        -netdev user,id=net0 \
        -device virtio-net-pci,netdev=net0 \
        -nographic
    ```

    The UEFI firmware, GRUB menu, and kernel messages will all appear in your terminal. Press `Ctrl+A` then `X` to exit QEMU.

## Performance expectations

TCG emulation of ARM64 on AMD64 is inherently slow. What to expect:

* **Boot time**: The installer may take several minutes to reach the desktop.
* **Responsiveness**: GUI operations will feel sluggish compared to native or KVM-accelerated virtual machines.
* **CPU usage**: The host CPU will run at high utilization during emulation.

For development and testing purposes, this setup is fully functional.
