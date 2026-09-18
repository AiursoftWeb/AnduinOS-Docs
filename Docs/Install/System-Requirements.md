# Can my computer run AnduinOS?

These requirements describe AnduinOS 2. Check the architecture before downloading an ISO. Meeting the memory and CPU requirements does not guarantee that every Wi-Fi adapter, GPU, or peripheral has a working driver.

| Component | Minimum | Recommended |
| --- | --- | --- |
| CPU | 64-bit x86_64 (AMD64) or ARM64, 2 GHz | 2.5 GHz quad-core |
| Memory | 4 GB RAM | 8 GB RAM |
| Storage | 25 GiB | 50 GiB, with additional room for applications and files |
| Display | 1024 × 768 | 2560 × 1440, 27-inch display |
| Boot firmware | AMD64: BIOS or UEFI; ARM64: UEFI/ACPI | UEFI with Secure Boot |
| Installation media | USB drive or DVD suitable for the selected ISO | USB drive and Internet access for updates |

The CPU, memory, storage and display figures follow the [AnduinOS download website](https://www.anduinos.com/). An SSD is helpful on an older computer. Large browser sessions, virtual machines, games and local AI models can require substantially more resources.

## Is there a 32-bit version?

The current images are AMD64 and ARM64. There is no current 32-bit x86 installation image. “AMD64” also works on compatible 64-bit Intel processors; it does not mean an AMD processor is required. Running a 32-bit application through compatibility packages is different from installing the operating system on a 32-bit-only CPU.

On an existing Linux installation, inspect the hardware with `lscpu`. Check the CPU's supported operating modes, not only whether the currently installed OS is 32-bit. In Windows, inspect **Settings → System → About → System type**.

## ARM computers, Raspberry Pi and Macs

The ARM64 image targets standards-based UEFI/ACPI machines. An ARM CPU alone is insufficient: board-specific boot firmware and device support also matter. Do not assume the generic image works on Raspberry Pi or Apple Silicon. See [ARM64 in QEMU](../Virtualization/ARM64-In-QEMU.md) for a documented virtual-machine setup.

For an Intel Mac, choose AMD64 and test a Live USB first. Keyboard, Wi-Fi, audio and model-specific firmware support need checking. This guide does not establish native Apple Silicon or every Intel Mac model as supported.

## BIOS, UEFI and old computers

AMD64 media supports BIOS and UEFI; ARM64 uses UEFI only. Secure Boot applies to UEFI, not Legacy BIOS. For dual boot, follow the [Windows coexistence guide](./Dual-Boot-With-Windows.md) and keep the boot mode consistent with the existing installation.

Before replacing an older OS, [create a Live USB](./Burn-A-USB-Stick.md) and test networking, sound, display, keyboard and suspend. Keep a backup and recovery media for the old OS. If essential hardware does not work, collect its model and device ID using the [troubleshooting guide](./Troubleshooting.md) before installing.
