# Recovery Environment: Design and Maintenance

The AnduinOS Recovery Environment is a small, independent Linux system for restoring Btrfs system snapshots when the installed operating system cannot boot. Select **AnduinOS Recovery Environment** in GRUB, choose a snapshot, confirm restoration, and restart. A Live USB and network connection are not required for this workflow.

This feature is introduced for new AMD64 and ARM64 installations in **2.0.6**. It requires the installer's **Erase disk** option with a supported, unencrypted, single-device Btrfs layout using `@root` and `@snapshots`. Ordinary upgrades do not create a recovery partition. Ext4 and reused-partition installations do not receive this feature automatically.

For everyday snapshot management, see [Disk Snapshots Manager](../../Applications/System/Disk-Snapshots-Manager/Disk-Snapshots-Manager.md). For EFI files, MOK enrollment, and bootloader repair, see the [boot-stack and signing guide](../../Install/Secure-Boot-Signing-Architecture.md).

!!! important "Recovery boundaries"

    The recovery environment can work despite damage to the installed kernel, initramfs, or startup programs. It still needs a working GRUB boot path, a readable recovery volume, and usable snapshots on the system disk. It cannot recover a failed disk from snapshots stored on that same disk. Keep an [independent backup](../../Install/Backup-And-Restore.md). Secure Boot qualification is described [below](#secure-boot-and-integrity).

## What runs during recovery

GRUB loads a separate kernel and a compressed initramfs from the recovery partition. The kernel unpacks the [initramfs archive](https://www.kernel.org/doc/html/latest/filesystems/ramfs-rootfs-initramfs.html) into memory and starts its `/init`. All recovery programs come from that image; the environment does not execute programs from the installed system.

| Component | Purpose |
|---|---|
| Ubuntu generic kernel and matching modules | Access storage, Btrfs/ext4, keyboard/mouse, and basic display devices. |
| BusyBox | Supply the shell and basic mount, device-module, synchronization, and restart commands. |
| `btrfs`, `blkid`, `flock`, and `jq` | Operate on snapshots, identify filesystems, serialize recovery actions, and read records. |
| Rust offline recovery engine | Reuse Disk Snapshots Manager's system-rollback logic. |
| C/LVGL graphical browser | Display snapshot selection, confirmation, progress, and restart controls directly through DRM/framebuffer. |
| Selected libraries, fonts, cursor, and scripts | Provide the runtime, snapshot-title rendering, and startup/action integration. |

The recovery image contains the tools, not the snapshots. Snapshots remain on the Btrfs filesystem. The graphical interface offers system recovery; it does not create new backup snapshots or restore Home. Its interface is currently in English, with fonts for displaying Chinese snapshot titles. If graphical startup fails, a text menu is available, provided the required display and input support works.

## How the image is built

The `anduinos-recovery-env` package recipe builds the payload separately for each architecture:

1. APKG validates Ubuntu package inputs using the configured Ubuntu archive signing key and repository checksums. It extracts the generic kernel, matching kernel modules, tools, and runtime libraries. The kernel is copied from its Ubuntu package rather than rebuilt locally.
2. Cargo compiles the existing Rust offline recovery engine. CMake and the target C/C++ toolchain compile the LVGL browser. The build selects the storage, filesystem, input, and display modules and includes their dependencies.
3. The build assembles a minimal root directory, checks ELF library dependencies, and packs it as a `newc` cpio archive compressed with gzip. The resulting file is named `initrd.img`; its contents use the initramfs archive format.
4. The package includes `vmlinuz`, `initrd.img`, and a generated `manifest.json`. The manifest records the architecture, kernel version, and both image files' SHA256 values. Input records and licenses accompany the package under `/usr/share/doc/anduinos-recovery-env/`.

The package is built through the repository's normal `apkg build --all` workflow, with the required Rust targets, target toolchains, CMake, `cpio`, `gzip`, `kmod`, `zstd`, and binutils available. The build assembles extracted target files without running the target programs or their maintainer scripts in a build chroot. This is separate from installing the finished package into the ISO's root filesystem.

Installing the finished package does not compile a kernel or graphical browser on the user's computer. Updating the installed system's ordinary kernel also does not rebuild this independent recovery kernel. Maintainers must rebuild and increment the recovery package when updating its embedded engine, runtime, drivers, or other image contents.

## Filesystems, files, and ownership

New supported installations reserve **256 MiB** for an **ext4** filesystem labelled **`AOS_RECOVERY`**. The system root and snapshot store use Btrfs. The recovery partition has no permanent mount point or `fstab` entry; deployment mounts it temporarily and unmounts it afterward.

An inspection mount shows a layout such as:

```text
recovery-volume/
├── lost+found/
└── anduinos-recovery-env/
    ├── owner.json
    ├── current -> payload-xxxxxxxx
    └── payload-xxxxxxxx/
        ├── vmlinuz
        ├── initrd.img
        └── manifest.json
```

| Item | Meaning |
|---|---|
| `lost+found` | ext4's filesystem-repair directory. |
| `owner.json` | The schema version and the root/recovery filesystem UUIDs that own this deployment. |
| `payload-xxxxxxxx` | One complete deployed payload. The suffix is a generated directory identifier, not a release version. |
| `current` | A relative symbolic link selecting the complete active payload. It does not duplicate the image files. |
| `manifest.json` | Architecture, kernel version, and image checksums for deployment verification. |

The installed system also holds these files:

| Path | Responsibility |
|---|---|
| `/usr/lib/anduinos-recovery-env/` | The source payload installed by dpkg from the package. |
| `/usr/libexec/anduinos-recovery-env` | The deployment, GRUB-generation, and successful-boot-recording helper. |
| `/var/lib/anduinos-recovery-env/volume.json` | The installed system's root/recovery UUID binding. |
| `/etc/grub.d/42_anduinos_recovery` | The script that generates the recovery menu entry during `update-grub`. |

For the same build and architecture, the kernel and initramfs can be reused across computers. The UUID bindings are generated per installation outside those images. The ext4 volume is writable during updates; the payload files are not an immutable filesystem merely because recovery normally reads them.

## How GRUB and recovery find the correct partitions

The binding contains two different filesystem UUIDs:

| Field | Used for |
|---|---|
| `volume_uuid` | GRUB finds the ext4 recovery filesystem and loads its kernel/initramfs. |
| `root_uuid` | The running recovery environment finds the Btrfs system filesystem to restore. |

During `update-grub`, `42_anduinos_recovery` calls the helper's `grub` command. The helper reads `volume.json` and emits the **AnduinOS Recovery Environment** menu entry into the generated GRUB configuration. Without that binding it emits no entry.

The generated entry searches for `volume_uuid`, loads both images through `anduinos-recovery-env/current/`, and passes `root_uuid` as the kernel parameter `anduinos.recovery.root=...`.

```text
GRUB configuration on the installed system
  -> search for recovery filesystem UUID
  -> load current/vmlinuz and current/initrd.img
  -> pass anduinos.recovery.root=SYSTEM_FILESYSTEM_UUID
  -> recovery locates that Btrfs filesystem
  -> read @snapshots and restore the selected system snapshot
```

Recovery reads the parameter from `/proc/cmdline`, requires one valid UUID, and uses `blkid` to locate exactly one matching device. Missing or duplicate devices cause an error. It rechecks the device UUID before mounting the Btrfs top level with `subvolid=5`. Browsing uses a read-only mount with log replay disabled; restoration mounts the target writable and invokes the offline engine.

The in-memory environment does not need the installed system's `volume.json` to find its target: GRUB has already passed the target UUID. `owner.json` is checked during deployment and updates; it is not the running recovery environment's device-selection input.

## ISO construction, installation, and chroot

dpkg unpacks the package into ordinary paths. A root-run maintainer script can then mount another filesystem and copy files there. The package never creates or formats partitions itself.

| Stage | What happens |
|---|---|
| ISO construction | The finished package puts its payload and helper into the ISO's temporary root filesystem. Its `postinst` calls `deploy --if-present`. With no binding and no recognized standard Btrfs root, deployment skips before mounting a recovery volume. |
| Supported fresh installation | The installer creates and formats the 256 MiB ext4 partition, copies the system, obtains the planned partition's UUID, and explicitly deploys to that UUID before generating GRUB. |
| Later package configuration/upgrades | `postinst` reuses the recorded binding, stages the new payload on that volume, unmounts it, and regenerates GRUB. |

The installer's explicit deployment call has this form; the target directory and UUID are supplied by the installation plan:

```text
chroot TARGET_ROOT /usr/libexec/anduinos-recovery-env deploy --volume-uuid RECOVERY_UUID
```

Deployment checks the actual root layout, target filesystem type and label, UUID binding, ownership, and mount state. In automatic unbound discovery, it also checks that the recovery volume is on the system disk. An already-mounted recovery volume is rejected. If the installer cannot deploy this optional component, it reports a warning; finishing installation does not by itself prove recovery deployment succeeded.

`--if-present` does not mean every chroot skips deployment. It permits an unconfigured image with no suitable target to skip. A repair chroot exposing a valid root and recovery volume can perform a real update. A cloned image retaining `volume.json` but lacking its original devices can fail package configuration because the existing binding is checked strictly. Valid unbound automatic discovery can also deploy when its conditions are met.

[Chroot changes pathname resolution](https://man7.org/linux/man-pages/man2/chroot.2.html); it does not isolate block devices or mount operations. Do not use it as assurance that maintainer scripts cannot access disks. Initial package configuration enables the successful-boot service through `systemctl --root=/ enable`, without starting it in the chroot. Later upgrades preserve a user's decision to disable the service.

## Why updates use a directory pointer

The deployment helper temporarily mounts the recovery volume under `/run/anduinos-recovery-*` and performs this sequence:

1. Validate the packaged payload and the target's ownership.
2. Check for enough free space to stage the replacement while retaining the current image.
3. Create a new `payload-*` directory and copy both images and the manifest.
4. Flush the files, read back their checksums, and synchronize the filesystem.
5. Create `current.new` and atomically replace `current`, selecting the entire new directory.
6. Synchronize, remove old payload directories, synchronize again, and unmount the volume.
7. Write the installed system's binding. Package configuration then runs `update-grub`.

Selecting a directory together keeps the kernel and initramfs paired. A failed copy or checksum check before pointer replacement leaves the previous active payload selected. Normal successful upgrades retain only the new payload, rather than accumulating one copy per package version.

The current build limit is **100 MiB for kernel plus initramfs**. Deployment requires free space for the complete new payload, including its manifest, plus **4 MiB**; the existing payload remains allocated during staging. Filesystem metadata and reserved space also use some of the partition. Insufficient space causes an error instead of deleting the current image to make room.

An interrupted update can leave temporary directories. Arbitrary physical power-loss behavior has not been fully qualified. Do not delete all `payload-*` directories or change `current` manually as routine maintenance: identify the active target and any operation in progress first. The pointer mechanism is replacement protection, not a user-facing archive of older recovery environments.

## The Last successful boot marker

The installed system's `anduinos-recovery-boot.service` records an advisory checkpoint in:

```text
/.snapshots/anduinos-btrfs-snapshots-manager/last-successful-boot.json
```

The recorder checks the configured root and snapshot store, avoids unfinished recovery transactions, and selects an available recovery point from the current history branch that existed before this boot began. It records the checkpoint only after a local graphical greeter or user session becomes active and the snapshot's identity and read-only state are verified. It does not create a new snapshot, run `update-grub`, or mount/write the recovery partition.

The recovery browser verifies this record before displaying **Last successful boot**. A missing, invalid, or no-longer-available record leaves the marker absent. The marker helps selection; it is not an independent boot test or guarantee that the marked snapshot will boot. A newer snapshot created after startup does not immediately replace this boot's checkpoint.

## Inspect an existing installation

These commands inspect an already-provisioned system. They do not create a recovery partition or migrate an older installation. Run the commands in this section on the installed system, not inside the minimal recovery image.

Check the installed package version:

```bash
dpkg-query -W anduinos-recovery-env
```

Read the binding. If this file is absent, stop: the following steps assume deployment has completed.

```bash
sudo cat /var/lib/anduinos-recovery-env/volume.json
```

Inspect the root and disk layout. Confirm the root UUID matches `root_uuid`, and the ext4 `AOS_RECOVERY` filesystem matches `volume_uuid`. Stop if either UUID is missing or appears on more than one device.

```bash
findmnt --target / --output FSTYPE,UUID,FSROOT
```

```bash
lsblk -o NAME,SIZE,FSTYPE,LABEL,UUID,MOUNTPOINTS
```

Read the configured recovery UUID into a shell variable:

```bash
RECOVERY_UUID=$(sudo python3 -c 'import json; print(json.load(open("/var/lib/anduinos-recovery-env/volume.json"))["volume_uuid"])')
```

Check whether it is already mounted. No output and exit status 1 are expected for an unmounted volume. If it reports a mount, finish that operation before continuing.

```bash
findmnt --source "UUID=$RECOVERY_UUID"
```

Use an empty, unused directory for inspection. The following example uses `/mnt/anduinos-recovery-inspect`; do not mount over another operation's files or mount point.

```bash
sudo mkdir -p /mnt/anduinos-recovery-inspect
```

Mount the healthy volume read-only. As described in the [ext4 mount options](https://www.kernel.org/doc/html/latest/admin-guide/ext4.html#options), `noload` also prevents journal replay; `ro` alone can still replay the journal. If the filesystem is damaged, investigate it separately rather than treating these options as a repair.

```bash
sudo mount -t ext4 -o ro,noload,nodev,nosuid,noexec "UUID=$RECOVERY_UUID" /mnt/anduinos-recovery-inspect
```

Inspect the active pointer and compare `owner.json` with the installed system's binding:

```bash
sudo ls -la /mnt/anduinos-recovery-inspect/anduinos-recovery-env/
```

```bash
sudo cat /mnt/anduinos-recovery-inspect/anduinos-recovery-env/owner.json
```

Read the active manifest, then compare its `files` hashes with the computed values:

```bash
sudo cat /mnt/anduinos-recovery-inspect/anduinos-recovery-env/current/manifest.json
```

```bash
sudo sha256sum /mnt/anduinos-recovery-inspect/anduinos-recovery-env/current/vmlinuz /mnt/anduinos-recovery-inspect/anduinos-recovery-env/current/initrd.img
```

Check the volume's actual free space:

```bash
df -h /mnt/anduinos-recovery-inspect
```

Unmount when finished, including after a failed inspection. Package deployment rejects a volume left mounted for inspection.

```bash
sudo umount /mnt/anduinos-recovery-inspect
```

## Refresh or remove the deployed environment

Normal package upgrades deploy automatically. To redeploy the currently installed payload on a system with a verified existing binding, first unmount any inspection mount, then run:

```bash
sudo /usr/libexec/anduinos-recovery-env deploy
```

Only after deployment succeeds, regenerate the GRUB menu:

```bash
sudo update-grub
```

This uses the installed package's payload; it does not download a newer recovery kernel. Use the normal APT update process to obtain newer published package versions. Do not edit UUID records or relabel an unrelated filesystem to bypass a deployment error. This procedure is not an initial-provisioning recipe for existing installations.

Removing or purging `anduinos-recovery-env` disables its boot-marker service and regenerates GRUB without the package's recovery menu hook. It leaves the separate partition and its files intact, so it does not reclaim the 256 MiB of disk layout. Partition deletion or resizing is a separate operation.

## Troubleshooting

| Symptom | Check |
|---|---|
| No recovery menu entry | Check whether the package and binding exist, whether the installer reported a recovery warning, and whether the last deployment and `update-grub` succeeded. |
| Deployment requests that the volume be unmounted | Close any manual inspection mount before retrying. |
| Volume absent, ambiguous, or owned by another installation | Compare both recorded UUIDs with `lsblk`. Cloned disks can duplicate UUIDs. Do not force a different volume into the binding. |
| Not enough space to stage an update | Inspect free space and the active pointer. Normal staging needs old and new payloads together. Investigate interrupted deployments before considering cleanup. |
| Architecture or checksum mismatch | Verify the installed package and source payload. Do not replace the expected hash merely to accept a damaged file. |
| Package configuration fails inside a cloned chroot | Check stale bindings, the root layout, device visibility, and mount permissions. A bound installation is not silently treated as a blank ISO image. |
| Graphical startup or pointer input fails | Try supported keyboard controls or the text fallback. Hardware needs appropriate recovery-image drivers; a working desktop driver does not establish recovery-image support. |
| Last successful boot marker absent | Check that the snapshot still exists and that a successful graphical boot could record it. Do not fabricate the marker to claim a snapshot is bootable. |
| Recovery reports a pending interrupted restore | Use its offered resume workflow. Do not delete transaction records to hide the pending operation. |
| GRUB itself or its configuration cannot be loaded | Use external installation/recovery media and the boot-repair workflow; the recovery menu depends on the bootloader being reachable. |

## Secure Boot and integrity

The recovery workflow has been validated with **Secure Boot disabled** on AMD64 and ARM64. Startup with Secure Boot enabled has not yet been verified. Boot-time authentication of this custom recovery initramfs is not implemented.

The package uses Ubuntu's kernel binary and checks image hashes during deployment. These checks detect corruption; they do not provide a signed, boot-enforced chain of trust for the whole recovery environment. [Ubuntu's traditional shim/GRUB path](https://documentation.ubuntu.com/security/security-features/platform-protections/secure-boot/#booting-with-grub) validates the kernel but does not validate an external initrd. An unsigned initrd alone therefore does not establish whether this particular recovery path can boot with Secure Boot enabled. Successful startup and complete image authentication are separate acceptance requirements.

## Implementation and upstream references

* [Recovery package, builder, deployment helper, and startup scripts](https://gitlab.aiursoft.com/aiursoft/anduinos-packages/-/tree/master/anduinos-recovery-env)
* [Installer deployment integration](https://gitlab.aiursoft.com/aiursoft/anduinos-packages/-/blob/master/anduinos-installer-beta/src/installer_core/snapshots_manager.py)
* [Linux initramfs design](https://www.kernel.org/doc/html/latest/filesystems/ramfs-rootfs-initramfs.html)
* [Linux ext4 mount options](https://www.kernel.org/doc/html/latest/admin-guide/ext4.html#options)
* [Linux chroot semantics](https://man7.org/linux/man-pages/man2/chroot.2.html)
* [Ubuntu Secure Boot validation](https://documentation.ubuntu.com/security/security-features/platform-protections/secure-boot/#booting-with-grub)
