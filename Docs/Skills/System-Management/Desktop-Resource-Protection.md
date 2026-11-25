# Desktop Resource Protection

Desktop resource protection is enabled by default. Keep using your applications and terminal commands as usual; the system automatically gives the desktop priority when resources are busy.

When the computer has spare resources, other work can use them normally. When you interact with a busy desktop, a heavy job may take a little longer so the desktop can respond promptly.

## Change the setting

Open **Control Panel → System → Resource Allocation Settings**.

Leave **Prioritize resources needed by the desktop (recommended)** enabled for normal use. Select **Apply** and authorize any change. Settings also apply after signing in again, restarting and upgrading. **Close** discards unapplied edits.

Advanced Options is collapsed when the window opens. Most users can leave its two settings at their recommended values:

| Setting | Recommended value | Purpose |
| --- | --- | --- |
| Desktop memory protection | 250 MiB | Helps keep the desktop's working memory available. This does not reserve RAM or limit application memory. |
| Foreground application priority | Recommended | Gives the application you are using more opportunity to run when applications compete for resources. |

Applying a change displays progress. If it fails, the window shows the error; correct the problem and try Apply again. **Restore Recommended Settings**, followed by **Apply**, restores the switch and these two controls.

Turning protection off retains your tuning choices. Memory-pressure handling and notifications remain enabled. Swap settings are managed separately in [Virtual Memory Control](../../Applications/System/Virtual-Memory-Control/Virtual-Memory-Control.md).

## When memory runs out

If memory pressure becomes severe, the system may stop an application. GNOME shows a notification explaining what happened. An entire application or terminal job can be affected.

## Configuration and removal

Machine settings are stored in **`/etc/uresourced.conf`**. The settings window and manual edits use this same file. After a manual edit, select Apply in the window or restart the computer.

Removing Control Panel leaves the protection service and its settings in place. Removing `anduinos-uresourced` stops the service and retains the configuration for reinstalling. Purging the package also removes its configuration. Package upgrades follow the usual dpkg rules for locally edited configuration files.

<details markdown="1">
<summary>Advanced: configuration and troubleshooting</summary>

These settings require `anduinos-uresourced` 0.5.5-2 or later and the corresponding Control Panel update. The desktop installation recommends the backend; the window offers installation if it is missing.

Advanced Output shows saved values, configuration paths and service errors. Saving formats the INI file and can change comments. A successful save remains in place if applying it to a service fails.

The recommended memory protection is subject to a shared budget of 10% of physical RAM across active users. I/O priority effects depend on storage support. Resource management follows upstream startup and shutdown behavior without snapshots of previous runtime settings.

Upstream also recognizes a personal `~/.config/uresourced.conf` (or its XDG equivalent) for application policy. It replaces the system application configuration. The window reports such overrides and leaves the personal file untouched. Restore Recommended Settings changes only the controls in the machine configuration.

The fixed memory-pressure policy monitors application and background groups at 80% memory PSI for 20 seconds. PSI measures stalled time, not RAM utilization. The desktop-session group is outside those two monitored groups; administrator changes can alter the scope. The kernel OOM handler remains the final fallback. Use `oomctl` and the system journal when investigating memory-pressure termination.

For swap diagnostics, see [Swap Control Strategy](Swap-Control-Strategy.md).

</details>
