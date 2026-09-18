# Update AnduinOS or migrate from 1.x to 2

An application update, an AnduinOS 2 package update, and migration from AnduinOS 1 to 2 are different operations. Start by checking:

```bash
cat /etc/os-release
df -h / /boot
```

## Already using AnduinOS 2?

Use App Store or the [normal APT update procedure](./Update-Your-System.md). The legacy `do_anduinos_upgrade` and `do-anduinos-autorepair` tools are retired on AnduinOS 2. Do not reinstall old scripts to update a 2.x machine.

## Migrating from 1.3 or 1.4

The [official migration guide](https://www.anduinos.com/MigrateFrom1x.html) describes migration from **1.3.9 or 1.4.2 to 2.0.2** using the legacy upgrade tool on the old system. Check that guide for the current eligible starting versions and target before proceeding. Ordinary `apt upgrade` on 1.x is not a substitute for this migration. The website describes a 2.0.2 destination, while the reviewed 1.3 migration script still writes 2.0.0 release metadata. Treat successful migration and subsequent package updates as separate checks; inspect the installed version rather than assuming that the advertised target has already been reached.

1. Make an [independent backup](./Backup-And-Restore.md), then open several files from it to verify recovery. Include documents, browser profiles/bookmarks, SSH and GPG keys, application data and necessary service configuration. Store credentials securely.
2. Record installed applications and third-party repositories. Keep configuration backups for reference; do not restore all of `/etc` or old GNOME settings over the new OS.
3. Confirm that your installed version is an eligible starting version. If it is older, consult the official guide for its update route before running an upgrade tool; do not assume the command will stop at an intermediate 1.x release. Make the backup above before any upgrade.
4. Connect to reliable power and Internet. The migration guide calls for at least 3 GB free in `/`; leave additional space for your installation and check `/boot` too.
5. Install `tmux` if needed, start `tmux new -s anduinos-migration`, and run `sudo do_anduinos_upgrade` **inside that session on the eligible 1.x system**. The desktop may restart during migration. Reattach with `tmux attach -t anduinos-migration` after logging back in; do not launch a second upgrade.
6. Follow the tool's output. Reboot after successful completion, then check `/etc/os-release`, refresh package metadata and apply normal AnduinOS 2 updates.

If the tool is missing or rejects the starting version, stop and consult the migration guide. Do not work around version checks by manually changing repository codenames. A migration can fail; source-list backups made by an upgrade tool are not backups of your personal data.

## What about upgrading 1.1 or 1.2 to 2?

The migration guide above does not document those as direct starting versions. Do not run a 1.3/1.4 migration script against 1.1 or 1.2. A clean installation of a suitable current image, followed by selective restoration of your data, is an alternative. If you need an in-place route, obtain version-specific guidance before changing the old system.

## Clean installation and what to restore

[Download and verify the ISO](./Download-AnduinOS.md), test a Live session, and follow the [installation guide](./Install-AnduinOS-From-USB.md). Review target disks carefully: erase installation removes data on its target. Disconnect a completed external backup during installation to avoid choosing it accidentally.

Restore personal documents first. Reinstall applications from sources intended for the new release, then restore their data selectively. Check key ownership and permissions, browser access, network shares and service configurations. Keep the old backup until you have tested your normal work.

## Verify migration and handle failure

Check networking, sound, graphics, login, printing and your essential applications. Review third-party sources rather than enabling an obsolete PPA blindly. Inspect `sudo dpkg --audit` for incomplete packages. If an upgrade stops, preserve the exact error and use [update and recovery troubleshooting](./Troubleshoot-Updates-and-Recovery.md); do not repeatedly rerun migration or reboot while it is still working.
