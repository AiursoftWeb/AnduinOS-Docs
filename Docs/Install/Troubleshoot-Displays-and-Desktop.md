# Black screen, external monitor freezes or desktop settings are broken

## Confirm the version and symptom

Record the [system version](./Troubleshooting.md), GPU, connected monitors and when the failure occurs: before login, after login, after attaching a monitor, or after suspend. Note whether the monitor says “no signal” or shows a lit black image.

## Simple checks

Check power, input selection and cable seating. Disconnect a dock or second monitor and try a direct cable. If the desktop is usable, open **Settings → Displays** and test a supported resolution, refresh rate and scale. See [display sizing](./Text-Icons-and-Displays.md).

For a missing taskbar or icons, open AnduinOS Appearance and check its layout and widget switches. Sign out and back in after saving work. Do not delete the whole user configuration to repair a single extension.

## Collect diagnostic information

From a working terminal or [text console](../Skills/System-Management/Terminal-Mode.md), inspect:

```bash
lspci -nnk
journalctl -b -k
systemctl status display-manager
journalctl -b -u gdm3 --since '-10 minutes'
```

Inside the affected graphical session, `echo "$XDG_SESSION_TYPE"` reports its session type and `gnome-extensions list --enabled` lists enabled extensions. A text console's session type does not describe a separate graphical login.

## Choose the next step

- **After a graphics-driver change:** inspect Driver Center and follow the [NVIDIA guide](./Install-Nvidia-Drivers.md) where applicable. With Secure Boot, check module trust in the [Secure Boot guide](./First-Boot-For-Secure-Boot.md).
- **Only with a second display or dock:** test one monitor at a time and a lower supported refresh rate. Record the working and failing combinations. This also applies to AMD graphics; installing an NVIDIA driver is not a generic display fix.
- **Only one user's desktop fails:** disable the recently added extension through Extensions and log in again. Re-enable it if it was unrelated. Test a separate user account if available before resetting settings.
- **After sleep:** collect logs around resume and use [sleep diagnostics](../Skills/System-Management/Diagnose-Sleep.md).
- **No graphical login at all:** try a text console. If the computer cannot boot far enough for one, use [boot recovery](./Troubleshoot-Updates-and-Recovery.md).

## When to ask for help

Report GPU IDs, driver, session type, monitor/dock/cable combination and the exact trigger. Include a photo of a pre-login error if logs cannot be obtained. Keep recovery steps specific to the failure; a blanket GNOME reset can remove working customizations without addressing a driver fault.
