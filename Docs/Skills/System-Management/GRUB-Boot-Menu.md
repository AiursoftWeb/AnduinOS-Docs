# GRUB boot menu: default operating system and display

Use **Control Panel → Startup and Boot** to choose which operating system starts automatically and how long the GRUB menu waits. These instructions apply to the AnduinOS 2 Control Panel; update through the normal system updater if your installed version lacks the default-system selector.

## Choose Windows or AnduinOS by default

1. Open **Startup and Boot** and authenticate if requested to read the boot menu.
2. In **Default operating system**, select an available entry such as Windows Boot Manager or AnduinOS. **Current setting (unchanged)** preserves your existing choice.
3. Set **Boot menu wait time** to a nonzero value, such as 10 seconds, so you have time to choose another entry.
4. Select **Apply**, authenticate, and wait for successful completion.
5. Save your work and restart. Let the countdown finish once to verify the default; on a second boot, select the other system manually.

This changes the default selection, not the visual ordering of every menu entry. It also does not change the firmware's UEFI boot-device order. If the computer goes straight into Windows without opening GRUB, select the AnduinOS boot entry in firmware first. See [dual boot](../../Install/Dual-Boot-With-Windows.md).

The Control Panel regenerates the menu itself. You do not need to run a second command after a successful Apply. The same selected delay also applies after an interrupted startup.

## Make a hidden GRUB menu visible

First set a nonzero wait time in Control Panel. If an older/custom configuration still hides the menu, inspect the timeout policy:

```bash
grep -nE '^[[:space:]]*(export[[:space:]]+)?GRUB_(TIMEOUT|TIMEOUT_STYLE|RECORDFAIL_TIMEOUT)=' /etc/default/grub /etc/default/grub.d/*.cfg
```

Later drop-in files can override `/etc/default/grub`. Control Panel maintains its own drop-in, so changing an earlier timeout assignment may have no effect.

For an explicit menu-visibility setting, create or edit this local drop-in:

```bash
sudoedit /etc/default/grub.d/99-local-menu-visibility.cfg
```

Put this one assignment in the file, preserving any intentional local settings already present:

```bash
GRUB_TIMEOUT_STYLE=menu
```

Regenerate the menu and check that the command finishes successfully:

```bash
sudo update-grub
```

If it reports an error, correct it before restarting. To undo this change, remove only the assignment you added, then run `sudo update-grub` again. Keep the wait time above zero while checking visibility.

## Windows is missing from the selector

The selector uses entries present in the generated GRUB menu. It does not install or repair Windows. Confirm Windows still boots from the firmware menu, then consult the [dual-boot guide](../../Install/Dual-Boot-With-Windows.md) for discovery and installation prerequisites. An encrypted or unavailable Windows volume, a different firmware boot mode, or disabled OS discovery requires diagnosis rather than a fabricated menu entry.

If Control Panel cannot read the entries, complete authentication or use **Retry**. Reopen the page after repairing/regenerating the boot menu. Do not delete recovery entries or replace AnduinOS boot packages to make the list shorter.

## Change text size and preserve recovery

Use **Display mode → Large text mode** for an unreadably small menu. **Automatic** lets firmware and GRUB choose a mode. See [GRUB Display Modes](./GRUB-Display-Modes.md) for details.

Do not edit `/boot/grub/grub.cfg` directly: it is generated and subsequent updates replace it. Avoid third-party menu rewriters that replace AnduinOS recovery hooks. A pending snapshot rollback may deliberately request a recovery boot; allow that operation to finish before changing boot defaults. For a damaged bootloader, use the [boot-stack recovery guidance](../../Install/Secure-Boot-Signing-Architecture.md), which is a different task from changing menu preferences.
