# Installation diagnostics (FAQ)

Use this page when booting installation media, running the installer, or starting the installed system for the first time. Choose the question that matches where startup stops. Try one change at a time and record the result.

| Symptom | Start here |
| --- | --- |
| USB does not appear in the boot menu, or media verification fails | [Check the installation media](#installation-media) |
| Want to enter the Live desktop without waiting for media verification | [Skip the startup check](#skip-media-check) |
| Live USB starts but the display becomes black or loses signal | [Try Safe Graphics](#live-black-screen) |
| Startup freezes at the splash screen or shows a `plymouthd` backtrace | [Try Console Compatibility](#plymouth-startup) |
| Installer stops while checking Secure Boot | [Check the firmware detection error](#secure-boot-detection) |
| Driver installation reports unmet dependencies | [Check the package source and versions](#driver-dependencies) |
| No target disk, unallocated space, or EFI partition is available | [Check the disk layout](#installation-disk) |
| Installation finished, but the installed system has a black screen | [Check the installed driver and boot state](#installed-black-screen) |

## Why does the USB not boot, or fail media verification? { #installation-media }

Check that the ISO matches your CPU architecture: AMD64 for compatible 64-bit Intel/AMD computers, or ARM64 for supported UEFI/ACPI ARM machines. See [System requirements](./System-Requirements.md).

If the USB is absent from the firmware boot menu, try another USB port and select its UEFI boot entry when available. Recreate the media using the [USB writing guide](./Burn-A-USB-Stick.md); with Rufus, use **DD mode**. If you used an intermediate boot tool such as Ventoy, testing a directly written USB helps isolate that layer.

An active **checking MD5 sums** screen is a media check, not by itself a startup failure. Let it finish while progress continues. If it reports a checksum or read error, verify the downloaded ISO against the checksum supplied with the release, then rewrite the USB or try another drive. A working USB on another computer does not rule out a port or read problem on this computer.

## The Live USB starts, then the screen goes black. What should I try? { #live-black-screen }

Check the monitor input and cable first. Try one directly connected display without a dock or adapter. Note whether the display reports **no signal** or remains lit with a black image.

Restart into the USB boot menu and choose **Advanced Options... → Try or Install AnduinOS (Safe Graphics)**. Use the wording shown in your menu if translated. This option uses `nomodeset` to avoid normal kernel graphics mode setting. It may provide a usable desktop with limited resolution or performance so you can investigate further.

If Safe Graphics also fails, or you see a `plymouthd` error, try [Console Compatibility](#plymouth-startup) separately. A black screen alone does not establish that the GPU driver is responsible.

If a desktop or text console becomes accessible, collect `lspci -nnk` and `journalctl -b -k`. See [Displays and desktop](./Troubleshoot-Displays-and-Desktop.md) for additional checks.

## Startup hangs at the splash screen or shows a `plymouthd` error. What should I choose? { #plymouth-startup }

Starting with AnduinOS **2.0.5** installation images, restart and select **Advanced Options... → Try or Install AnduinOS (Console Compatibility)**, below **Safe Graphics**. This option selects the on-screen kernel console with `console=tty0` and still attempts to start the graphical Live desktop. It keeps normal graphics initialization; Safe Graphics is a separate workaround and may not resolve this console-related failure.

This workaround has been verified on NVIDIA DGX Spark running the ARM64 Live image. The affected device range and frequency are not known, and the problem is not established as exclusive to that model. Continue using ordinary startup when it works. Choosing this option is a workaround, not proof that every splash-screen freeze has the same cause.

### My image has no Console Compatibility entry

Images older than 2.0.5 do not include this entry. Try the same parameter for one boot:

1. Highlight the ordinary Live startup entry for your language in GRUB. Open its submenu first if necessary.
2. Press <kbd>E</kbd> to edit it.
3. Find the line beginning with `linux` that loads `/LiveOS/vmlinuz`.
4. Add `console=tty0` before the existing `---`, with spaces on both sides. Keep the other parameters. For example, the end of the line may read `quiet splash console=tty0 ---`.
5. Press <kbd>Ctrl</kbd> + <kbd>X</kbd> or <kbd>F10</kbd> to boot.

The manual edit lasts for that boot only. If it works, record the successful parameter and the original error. If it fails, preserve a photo of the error and report which options you tried.

## Can I skip media verification and go straight to the Live desktop? { #skip-media-check }

Yes. Starting with AnduinOS **2.0.5** installation images, select **Advanced Options... → Try or Install AnduinOS (Skip Media Check)**, below **Console Compatibility**. It uses ordinary graphical startup and omits the startup media check. It does not disable Secure Boot or change graphics-driver selection.

The ordinary language entries, Safe Graphics, Console Compatibility, and To Go explicitly enable the startup check with `rd.anduinos.media-check=1`. Starting with 2.0.5 images, only the value `1` enables the check; an absent parameter or another value skips it. To combine skipping with another startup option, press <kbd>E</kbd> on that entry, remove `rd.anduinos.media-check=1` from the `linux` line, and boot with <kbd>Ctrl</kbd> + <kbd>X</kbd> or <kbd>F10</kbd>. The edit lasts for that boot only. Images older than 2.0.5 do not support this parameter or menu option.

With the interactive AnduinOS checker, you can also press <kbd>S</kbd> while a check is running to skip it and continue to the Live session.

**Skipping the startup check does not skip installation verification.** The installer checks the medium again before changing partitions and stops if verification fails. A skipped check is recorded as skipped, never as passed. If the startup check reported corruption or read errors, rewrite or replace the media before installing.

## The installer stops while determining Secure Boot state. Is my computer unsupported? { #secure-boot-detection }

An error such as `mokutil failed while determining the Secure Boot state` indicates a firmware-state detection failure. It does not by itself establish that AnduinOS cannot run on the computer. UEFI boot and support for Secure Boot are different properties.

Use the latest available installation image and retry. From a terminal in the Live environment, collect:

```bash
LC_ALL=C mokutil --sb-state
echo $?
ls -ld /sys/firmware/efi /sys/firmware/efi/efivars
```

Keep the output and exit code together. A missing EFI directory, unsupported Secure Boot, and an error accessing firmware variables are different cases. If the installer still stops, report the exact output and ISO version. Follow the [Secure Boot guide](./First-Boot-For-Secure-Boot.md) for supported firmware and certificate enrollment.

## Driver installation reports unmet dependencies. Should I force it? { #driver-dependencies }

First refresh package information:

```bash
sudo apt update
```

Resolve any download or repository errors before retrying the driver installation. If APT still reports incompatible required versions, use the [software-source guide](./Select-Best-Apt-Source.md) to try another mirror or the official Ubuntu archive for your architecture, refresh again, and retry. Keep the Ubuntu release codename and separate AnduinOS source unchanged.

Mirrors can retain an older repository snapshot, and an upstream publication can temporarily expose kernel modules before matching driver packages. A successful `apt update` verifies signed metadata and index integrity; it does not guarantee that the selected packages have satisfiable dependencies. Download speed alone does not establish that a mirror has the latest snapshot.

Preserve the first dependency error and compare the named packages with `apt-cache policy PACKAGE_NAME`, replacing `PACKAGE_NAME` with each package in the error. Do not force incompatible versions or enable a testing repository as a generic repair.

If the installer is still at its optional-components page, you can omit optional third-party drivers and system updates for the base installation, then configure the driver after the first boot. This does not guarantee that hardware requiring an additional driver will work immediately. See [Install drivers](./Install-Drivers.md) and [Install NVIDIA drivers](./Install-Nvidia-Drivers.md).

## The installer cannot find my disk or a suitable EFI partition. What should I check? { #installation-disk }

From the Live desktop, inspect the detected disks without modifying them:

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL
```

If the intended disk is absent, check whether firmware detects it and collect `journalctl -b -k`. If the disk is present but the coexistence page shows **(None)** for unallocated space or an EFI partition, the installer has not found a suitable layout for that route.

Use **Rescan and Reselect Disk** after preparing genuine unallocated space and the appropriate EFI layout. The installer does not shrink Windows for you. Follow [USB installation](./Install-AnduinOS-From-USB.md#keep-another-operating-system) and [Dual boot with Windows](./Dual-Boot-With-Windows.md) before changing partitions; a missing candidate is not a reason to format an existing Windows or EFI partition.

## Installation succeeded, but the first boot has a black screen. What now? { #installed-black-screen }

Confirm that the computer is booting the installed disk. The USB's Safe Graphics and Console Compatibility entries apply to Live startup; selecting them does not diagnose the installed system's driver or boot configuration.

If a text console is available, use the [terminal-mode guide](../Skills/System-Management/Terminal-Mode.md) and inspect:

```bash
uname -r
lspci -nnk
systemctl status display-manager
journalctl -b -k
```

For an installed NVIDIA driver, also run `nvidia-smi` and preserve any error. Check whether required MOK enrollment was completed using the [Secure Boot guide](./First-Boot-For-Secure-Boot.md). If GRUB offers an older installed kernel, test it and record the result. Continue with [display troubleshooting](./Troubleshoot-Displays-and-Desktop.md) or [boot recovery](./Troubleshoot-Updates-and-Recovery.md).

## What information should I include when asking for help?

Provide the exact ISO filename/version, computer model and architecture, the stage that fails, a photo or text of the first error, and the result of each startup option tried. If you reached the Live desktop, collect:

```bash
cat /etc/os-release
uname -r
cat /proc/cmdline
cat /proc/consoles
lspci -nnk
journalctl -b -p err
```

A Live session's logs describe that Live boot, not an earlier failure of the installed system. For an installer failure, preserve its detailed output and installer log before closing the window. See [Ask for help with useful evidence](./Troubleshooting.md#ask-for-help-with-useful-evidence) for reporting and log-sharing guidance.
