# Printer paused or scanner not found

## Confirm the version and symptom

Record the [system version](./Troubleshooting.md), exact device model, USB or network connection, and whether printing, scanning or both fail. A multifunction device can have one function supported while another needs a different backend.

## Simple checks

Check paper, ink, device display errors and connectivity. Resume a paused printer through **Settings → Printers** after fixing its physical error. Review its queue; cancel only the jobs you intend to discard. Do not repeatedly submit the same document to a paused queue.

For discovery failures, use the same local network instead of guest Wi-Fi. Verify that the device has enabled IPP/AirPrint for printing or eSCL/AirScan for scanning where supported. Test USB directly without a hub.

## Collect diagnostic information

```bash
lpstat -t
systemctl status cups
journalctl -b -u cups --since '-10 minutes'
lsusb
```

For scanning, run `scanimage -L` as the desktop user. If missing, install `sane-utils` from the configured APT source. An empty result means the installed backends did not discover a scanner; it does not prove the hardware is broken.

## Choose the next step

For printing, use [Managing Printers](./Managing-Printers.md). In Driver Center, confirm printing services are enabled. Re-add a stale printer configuration only after recording its address and settings. A network printer's address may have changed.

For scanning, follow [Scan documents](./Scanning-Documents.md) and check the exact model against SANE's device support list. For Canon 4400F or another older USB scanner, a related model's driver is not evidence of compatibility. If a vendor backend is required, verify its architecture and supported OS release before installing it.

If a scanner works over USB but not the network, inspect discovery and the device's service settings. Keep firewall changes specific to the documented service; [firewall status](./Enable-Firewall.md) helps separate policy from application failures.

## When to ask for help

Provide the model, USB ID or connection type, printer status, `scanimage -L` result and exact error. Say whether another computer can print or scan. Avoid publishing document contents or unredacted job names.
