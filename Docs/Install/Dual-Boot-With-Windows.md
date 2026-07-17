# Dual Boot AnduinOS with Windows

Before you begin, ensure you have a backup of your important data. Dual booting can lead to data loss if not done correctly.

!!! tip "Secure Boot Support"
    AnduinOS fully supports Secure Boot alongside Windows. If you plan to use it, please refer to our [Secure Boot Guide](./First-Boot-For-Secure-Boot.md) to understand the MOK enrollment process before installation.

## Two disks setup (Suggested)

If you have two separate physical disks, one for Windows and one for AnduinOS, follow these steps:

1. **Backup Data** and wipe all disks. Especially ensure the disk for AnduinOS is empty. You can do this by running:

```bash title="Wipe Disk"
sudo wipefs -a /dev/sdX
```

Replace `/dev/sdX` with the actual disk identifier for the AnduinOS disk (e.g., `/dev/nvme1n1`, `/dev/sdb`).

2. **Install Windows**: Install Windows on the first disk as you normally would. Don't mount or format the second disk in Windows.
3. **Install AnduinOS**: During the installation of AnduinOS, select the second disk as the installation target. Let AnduinOS take the entire disk (`Erase Disk`) and handle the partitioning automatically.
4. **Bootloader**: AnduinOS will automatically install the GRUB bootloader, which will detect Windows and add it to your boot menu.
5. **Enable BitLocker (Optional)**: If you want to use BitLocker on the Windows disk, you can safely enable it after the installation of AnduinOS.

!!! warning "Always install Windows first!"
    The Windows installer tends to aggressively overwrite the bootloader of other operating systems. Therefore, it is crucial to install Windows first! If you install AnduinOS first, you may need to rescue and reinstall the GRUB bootloader manually after installing Windows.

## Single disk setup

If you only have one physical disk, you will need to share it between Windows and AnduinOS:

1. **Backup Data**: Ensure you have a full backup of all important data before proceeding. Modifying partitions is always risky.
2. **Turn off Fast Startup**: In Windows, go to Control Panel > Power Options > Choose what the power buttons do > Change settings that are currently unavailable, and uncheck "Turn on fast startup (recommended)". This prevents Windows from locking the disk in hibernation mode.
3. **Turn off BitLocker**: If you have BitLocker enabled, you must suspend or decrypt it before resizing partitions.
4. **Prepare Free Space**:
    - *If you already have Windows installed:* Open "Disk Management" in Windows, right-click your Windows partition (usually `C:`), and select "Shrink Volume". Shrink it to create **Unallocated Space** for AnduinOS (at least 32 GB is recommended).
    - *If you are installing Windows from scratch:* During the Windows installation, leave enough unallocated space on the disk. Do not format the entire drive for Windows.
5. **Install AnduinOS**: Boot from the AnduinOS installation media. During the installation, select the **Install alongside** or **Replace a partition** option and choose the unallocated space you prepared. The installer will automatically format it and set up your system.

!!! warning "Always install Windows first!"
    Just like in the two-disk setup, install Windows first to prevent it from overwriting the AnduinOS GRUB bootloader!
