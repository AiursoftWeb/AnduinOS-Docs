# Btrfs snapshots: a practical backup and recovery walkthrough

Use AnduinOS's built-in **Disk Snapshots Manager** to keep local recovery points, retrieve an older document, or undo a broken system change. This walkthrough uses the existing manager; you do not need to install Timeshift or create a second snapshot layout.

It requires a supported AnduinOS Btrfs installation. An Ext4 installation cannot gain this workflow merely by installing the application. Open **Control Panel → Backup and Recovery → System Snapshots**. If the manager reports an unsupported layout, use [independent backups](../../Install/Backup-And-Restore.md) instead of manually creating its internal subvolumes.

## Understand the two histories

| Page | What a whole-snapshot rollback changes | What it preserves |
| --- | --- | --- |
| System Recovery | Operating-system files, system configuration and installed system packages | Current Home files and settings |
| Personal Files Recovery | All users' Home files and settings | The current operating-system root |

The two histories are independent. A System snapshot is not a backup of your documents. Other disks and separately managed data are not automatically included. Ordinary Btrfs snapshots do not recursively capture nested subvolumes.

Both histories normally live on the same disk as your current files. Copy important data to another device or backup service as well; a failed disk can destroy the live files and snapshots together.

## Create a checkpoint before a change

1. Save your work. Open **System Recovery** before a driver/package/system configuration change, or **Personal Files Recovery** before changing important Home content.
2. Choose **Create Snapshot Now** and complete any requested authentication.
3. Wait for the new snapshot to appear. Check its time and scope. Give it a recognizable name using the available rename action.
4. If you need it kept beyond normal retention, choose **Keep Forever** from its menu. Manual snapshots are otherwise eligible for automatic cleanup too.

AnduinOS normally creates a System snapshot before a real DPKG package transaction. That does not protect Home edits, Flatpak user data or every change you make between transactions. Make an explicit checkpoint when you need one.

## Practice recovering one file

Use a disposable text file in Documents for your first practice:

1. Create the file with a short sentence and save it.
2. Create a **Personal Files Recovery** snapshot and confirm it appears.
3. Change the sentence and save the file again.
4. In Files, right-click that file and select **View File History…**.
5. Browse the earlier version, then choose **Recover…** and select a separate destination/name.
6. Open the recovered copy and verify the original sentence. Check that the current file still has your later edit.

For a deleted file, open the containing folder's history using **Browse This Folder's History…**, or browse the snapshot from Personal Files Recovery. You can recover an ordinary file or folder without restarting or rolling back all of Home. History browsing is limited to your own local Home files; network paths, mounted external locations and special files are outside this workflow.

## Recover after a system change

If the desktop still starts, open **System Recovery** and select a healthy snapshot from before the problem. Save work and close applications before choosing **Roll Back**. Read the affected scope and authenticate.

Once preparation is armed, the manager starts an automatic **60-second restart countdown**. Be ready to restart; do not continue working on files while recovery is pending. Let recovery and the next boot finish without interrupting power.

The manager creates a safety snapshot first. An ordinary System rollback preserves Home and snapshot history, and the chosen recovery point can be reused. After login, verify the original symptom and inspect your current documents.

If the system cannot boot, consult the [Independent Recovery Environment](./Recovery-Environment.md) guide **only if your installation has that GRUB entry and meets its prerequisites**. That feature is documented for supported new 2.0.6 installations; ordinary upgrades do not create its recovery partition. Otherwise use the recovery options appropriate to your installation. Do not assume every AnduinOS 2 computer has an independent recovery environment.

## Restore all Home data only when intended

Choosing **Roll Back** on a Personal Files snapshot replaces **all users' Home files and settings**, not just the selected document or your own account. First copy newer files you want to keep to external storage. The manager checks account paths and ownership; nested Home subvolumes can block the operation.

For one lost document, use file history instead. For a complete return to the initial installation, read the separate [Factory Reset procedure](../../Applications/System/Disk-Snapshots-Manager/Disk-Snapshots-Manager.md#factory-reset), including its optional Home and history-deletion consequences.

## Configure automatic snapshots and storage

Open **Automatic Snapshots** on each recovery page. Enable the scopes you need, choose their freshness interval, and configure retention. Then verify that snapshots actually appear after the next eligible scheduler run. A sleeping computer catches up on a later check rather than creating every missed snapshot.

The shared **Minimum free space** setting defaults to **40 GiB**. Below it, scheduled creation pauses while enabled retention cleanup continues. On a smaller disk, choose a suitable reserve deliberately; setting it to zero removes this extra scheduler guard, not all safety checks. Manual, package and recovery snapshots have their own checks and are not disabled by that pause.

Protect a small number of important restore points and review old history periodically. Keep the installer-created **New OS** baselines for factory recovery. Delete unwanted snapshots through the manager, never by deleting its storage directories. See the [full manager reference](../../Applications/System/Disk-Snapshots-Manager/Disk-Snapshots-Manager.md) for retention buckets, size accounting and disk health, and [disk cleanup](./Disk-Cleanup.md) when space is low.
