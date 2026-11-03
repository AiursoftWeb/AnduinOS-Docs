# Disk cleanup and free-space maintenance

Looking for a system cleaner? Start by finding what occupies the disk. AnduinOS uses APT for system packages, Flatpak for many desktop apps, and, on supported Btrfs installations, separate snapshot history. Each needs its own cleanup method.

## Measure before deleting

In Files, review Downloads and Trash. Empty Trash only after checking its contents. For an overview in Terminal:

```bash
df -h /
```

Check Home separately in case it is on another filesystem:

```bash
df -h "$HOME"
```

Use [storage diagnosis](./Debug-Storage-Consumption.md) to locate large directories. On Btrfs, inspect the storage bar and **Information** in **Disk Snapshots Manager** too; snapshot sharing makes ordinary directory totals incomplete.

## Remove applications and unused downloads

Uninstall applications you no longer use in **Software → Installed**. This may preserve their user data; see [removing applications](../../Install/Installing-Applications.md). Review large ISO images, archived downloads and old project build outputs individually.

Clear downloaded APT package archives:

```bash
sudo apt clean
```

This removes cached package downloads, not installed applications. They will need downloading again if required later.

Preview automatically removable dependencies:

```bash
sudo apt --simulate autoremove
```

Read the proposed list. If it includes desktop metapackages, boot/recovery tools, drivers or applications you still need, stop and investigate why they are considered unused. Otherwise run the real operation and review its confirmation:

```bash
sudo apt autoremove
```

Do not add `-y` or manually delete kernel files. APT transactions can themselves create a pre-change system snapshot, so the immediate space gain may be smaller than expected.

For Flatpak applications installed for your user, review and remove unused runtimes:

```bash
flatpak uninstall --user --unused
```

For system-wide Flatpaks, do the same for that installation:

```bash
flatpak uninstall --system --unused
```

See the [Flatpak command guide](https://docs.flatpak.org/en/latest/using-flatpak.html) for installation scopes and unused runtimes. Read each proposed removal. Neither command is a request to erase all application data. AnduinOS 2 normally uses its App Store with Flatpak; do not install Snap merely to follow a generic Snap-cleanup tutorial.

## When deleting files does not free enough space

Btrfs snapshots may still reference deleted data. Open **Control Panel → Backup and Recovery → System Snapshots**, then inspect **both** System Recovery and Personal Files Recovery.

Delete only restore points you no longer need using the manager's deletion action. Review their dates and protection state first. Preserve **New OS** and a useful recent recovery point. Configure automatic retention independently for both scopes using the [snapshot tutorial](./Btrfs-Backup-and-Recovery.md).

A snapshot's apparent size is not its exclusive space consumption. Several snapshots can share the same blocks, and deleting one may release little space. Never manually remove the snapshot-store directories, run indiscriminate subvolume deletion, or use Factory Reset as a disk cleaner.

## Logs, developer caches and optional cleaners

Inspect journal usage before deciding whether it is responsible:

```bash
journalctl --disk-usage
```

Keep the logs needed to diagnose the problem. Routine space maintenance should not blindly purge them. If abnormal logging keeps filling the disk, fix its cause and choose a retention policy appropriate to that computer.

Use Android Studio's SDK/Device Manager to remove unused SDK images and virtual devices. For Rust, use `cargo clean` only inside the project whose generated build output you want to remove; future builds will take longer. Do not indiscriminately delete container volumes or virtual-machine disks.

BleachBit and similar tools are optional, not required AnduinOS maintenance. If you choose one, preview every selected category, close affected apps, and expect history, sessions or offline data to be lost where selected. Avoid administrator-wide cleaning and free-space wiping as routine maintenance, especially on snapshot-backed SSDs.

Finally, recheck `df` and the snapshot manager. Free-space recovery is the useful result; a cleaner reporting many deleted files is not enough.
