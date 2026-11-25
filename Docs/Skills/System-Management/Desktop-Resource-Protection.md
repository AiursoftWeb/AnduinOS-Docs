# Desktop Resource Protection

Desktop resource protection gives the desktop and focused applications a larger share of resources when work competes for CPU, memory, or supported disk I/O. GNOME explains when an application is stopped because of memory pressure.

These settings require `anduinos-uresourced` **0.5.5-2 or later** and the corresponding Control Panel update on AnduinOS 2.0 / 2.1. The desktop metapackage recommends the backend; the window offers to install it if missing.

## Change resource allocation

Open **Control Panel → System → Resource Allocation Settings**.

Leave **Prioritize resources needed by the desktop (recommended)** enabled for normal desktop use. Changes apply to all graphical users. Select **Apply** and authorize the change. Settings are always saved for future sign-ins, reboots and package upgrades. **Close** discards unapplied edits.

The window initially shows the switch and actual service state. Advanced options are collapsed; Apply is disabled until a setting changes or a service needs attention. Applying settings expands the output area.

| Advanced setting | Recommended value | Meaning |
| --- | --- | --- |
| Desktop memory protection | 250 MiB | Memory protected from reclamation, subject to the shared budget of 10% of physical RAM. It does not reserve RAM or limit application memory. The control accepts 32–4096 MiB. |
| Foreground application priority | Recommended | Relative CPU/I/O weights: Normal 100, Recommended 300, Higher 500. Ordinary applications use 100. These are contention shares, not speed multipliers. I/O effects depend on storage support. |

**Restore Recommended Settings**, followed by **Apply**, restores the switch and these two controls. Other configuration keys and personal files are left alone. Custom values remain unchanged until you edit their controls.

Apply uses ordinary service stop/start operations. If the configuration is saved but a service cannot start, the window reports the error and retains the saved settings. Correct the problem and apply again. Advanced Output shows progress, settings and configuration paths.

Disabling protection stops resource management. Upstream resets resources to its inactive/default settings; the package does not save and reconstruct arbitrary previous runtime properties. The switch does not disable `systemd-oomd`, kernel OOM handling or GNOME notifications. It does not change Zram, Zswap or swappiness; use [Virtual Memory Control](../../Applications/System/Virtual-Memory-Control/Virtual-Memory-Control.md) for those.

## One configuration file

The system configuration is **`/etc/uresourced.conf`**. Control Panel and administrators use this same upstream INI file. There is no `conf.d` hierarchy or generated effective configuration.

For example:

```ini
[AnduinOS]
Enabled=true

[Global]
MaxMemoryMin=10%

[ActiveUser]
MemoryMin=250M
CPUWeight=500
IOWeight=500

[AppBoost]
ActiveCPUWeight=300
ActiveIOWeight=300
BoostCPUWeightInc=200
BoostIOWeightInc=200
```

`[AnduinOS] Enabled` controls systemd startup of both resource-management instances; missing means enabled. Upstream ignores that section. The other settings use upstream names. `SessionSlice` normally inherits `ActiveUser` values; an explicit `SessionSlice` override can change the resulting session allocation.

Advanced users can edit the file directly:

```bash
sudoedit /etc/uresourced.conf
```

Apply the saved file:

```bash
sudo /usr/lib/anduinos-uresourced/helper apply
```

The GUI changes only its controlled keys and preserves other sections and values. Saving uses the standard INI writer, so formatting and comments can change.

Upstream also honors `$XDG_CONFIG_HOME/uresourced.conf`, normally `~/.config/uresourced.conf`, for personal application policy. If that file exists, it **replaces** the system application configuration. Missing application keys use upstream defaults (for example, active weights 100), not keys merged from the system file. The window reports personal overrides and leaves that file untouched. The machine-wide enable switch is always read from `/etc/uresourced.conf`.

## Restore or remove

The command-line equivalent of restoring the three GUI controls is:

```bash
sudo /usr/lib/anduinos-uresourced/helper reset
```

| Action | Result |
| --- | --- |
| Disable protection | Stop the services; retain the saved tuning values |
| Remove Control Panel | Retain backend operation and configuration |
| Remove `anduinos-uresourced` | Stop the services; retain `/etc/uresourced.conf` for reinstalling |
| Purge `anduinos-uresourced` | Remove its conffile using normal dpkg behavior |

Upgrades preserve local conffile changes according to dpkg's normal rules. Personal configuration is not package-owned. The upstream-generated `/run/systemd/user/session.slice.d/99-uresourced.conf` is removed when the system service stops; it is not another preferences file.

## Give heavy terminal jobs their own group

```bash
aos-bg make -j"$(nproc)"
```

This creates a unique scope under `background.slice`, preserving arguments and exit status. The interactive shell remains outside that job's OOM group. Appending `&` alone does not establish a separate resource group.

## Memory pressure and feedback

The package's standard `systemd-oomd` drop-ins monitor user `app.slice` and `background.slice` at **80% memory PSI for 20 seconds**. PSI measures stalled time, not RAM utilization. Base root and `user@.service` monitoring is cancelled, keeping `session.slice` outside these two monitored application trees. Other administrator-configured ancestors can still affect the scope; inspect `oomctl` on customized systems.

Memory-pressure termination affects a process group: a browser can be terminated as an entire application. System containers, VMs and services need their own resource budgets. The kernel OOM handler remains the final fallback.

The vendor files are:

```text
/usr/lib/systemd/user/app.slice.d/30-anduinos-resource-policy.conf
/usr/lib/systemd/user/background.slice.d/30-anduinos-resource-policy.conf
/usr/lib/systemd/system/user@.service.d/30-anduinos-resource-policy.conf
/usr/lib/systemd/system/-.slice.d/30-anduinos-resource-policy.conf
```

GNOME Settings Daemon already watches user services and scopes for `oom-kill` and displays the application-stopped notification. A MemoryMax limit can produce the same result, so the notification alone does not prove all physical RAM was exhausted.

## Inspect the actual state

```bash
/usr/lib/anduinos-uresourced/helper status
systemctl status uresourced.service systemd-oomd.service
systemctl --user status uresourced.service
systemctl --user show session.slice -p MemoryMin -p CPUWeight -p IOWeight
oomctl
journalctl -b -u uresourced.service -u systemd-oomd.service
journalctl --user -b -u uresourced.service
```

For swap configuration, see [Swap Control Strategy](Swap-Control-Strategy.md).
