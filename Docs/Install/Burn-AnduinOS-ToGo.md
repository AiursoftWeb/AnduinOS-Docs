# Keep files on a Live USB after reboot (AnduinOS ToGo)

**AnduinOS ToGo** lets you use installation media as a persistent portable operating system. Installed packages, system configuration changes, and saved files are retained on the USB drive after a reboot.

This is ideal for carrying your development environment or personal desktop configuration between different computers.

### Requirements

  * **ISO**: An AnduinOS installation image.
  * **USB Drive**: A flash drive with at least **16GB** of capacity. (The OS itself takes ~2.5GB, so 32GB or larger is highly recommended for a comfortable experience with installed software and user files).

### Creation Steps

The process creates a hybrid partition layout that supports persistence automatically.

1.  **Burn the ISO**: Follow the [Bare-metal Installation](./Burn-A-USB-Stick.md) steps to flash the ISO to your USB drive.

!!! warning "Critical: Block-level burning required"

    To support the persistence overlay partition, the ISO **must** be written block-by-block.
    * If you are using **BalenaEtcher** or **Impression**, you are already good to go (they do this natively).
    * If you are using **Rufus** on Windows, you **must select `dd` mode** when prompted before writing. "ISO mode" will **not** work.

2.  **Boot**: Insert the USB drive into the target computer and boot from it.
3.  **Select Language**: When the GRUB boot menu appears, use your arrow keys to select your preferred language (e.g., **English**) and press Enter.
4.  **Select Mode**: In the language sub-menu, **do not** select the default "Try or Install AnduinOS" option. Instead, navigate down and select **AnduinOS ToGo**.

The system will boot, automatically mount the persistent partition on the USB stick, and overlay it onto the root filesystem. Any changes you make will now be written back to the USB drive permanently.

### Verifying Storage Space

Since USB drives typically have less storage than internal hard drives, and the persistence partition shares space with the ISO image itself, it is highly recommended to check your available disk space immediately after booting.

Open a terminal and run:

```bash title="Check available persistent storage"
df -h /
```

Ensure you have enough `Avail` space before performing large updates or compiling large projects.
