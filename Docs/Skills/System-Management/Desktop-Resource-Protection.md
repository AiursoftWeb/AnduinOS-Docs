# Desktop Resource Protection

Desktop resource protection gives the desktop and focused applications a larger share of resources when work competes for CPU, memory, or supported disk I/O. It also keeps memory-pressure handling focused on application and background groups, while GNOME explains when an application is stopped because of memory pressure.

The settings described here require `anduinos-uresourced` **0.5.5-2 or later** and the corresponding Control Panel update on AnduinOS 2.0 / 2.1. The desktop metapackage recommends the backend. If it is missing, the settings window offers to install it.

## Change resource allocation

Open **Control Panel → System → Resource Allocation Settings**.

Leave **Prioritize resources needed by the desktop (recommended)** enabled for normal desktop use. Changes apply to all graphical users on this computer. Select **Apply** and authorize the change; the saved configuration also applies after signing in again, restarting, and upgrading packages. **Close** discards changes that have not been applied.

Expand **Advanced Options** for two adjustments:

| Setting | Default | Meaning |
| --- | --- | --- |
| Desktop memory protection | 250 MiB | An amount protected from memory reclamation. It does not preallocate RAM or limit application memory. All active users share a protection budget capped at 10% of physical RAM. |
| Foreground application priority | Recommended | Relative CPU and I/O weights of 100 (Normal), 300 (Recommended), or 500 (Higher). Ordinary applications use 100. A weight is a share during competition, not a guaranteed speed multiplier. |

The memory control accepts 32–4096 MiB. The actual protection can be smaller because of the shared budget. The I/O effect depends on the storage stack's support for weighted control.

**Advanced Output** shows progress, errors, effective values, and configuration sources. If administrator or personal configuration overrides a choice, the window reports that. A custom foreground weight is retained until you explicitly select a different value.

Disabling protection withdraws `uresourced` memory protection and scheduling boosts. It retains your tuning choices. It does not disable `systemd-oomd`, kernel OOM handling, or GNOME's OOM notifications, and it does not change Zram, Zswap, or swappiness. Configure those separately in [Virtual Memory Control](../../Applications/System/Virtual-Memory-Control/Virtual-Memory-Control.md).

## How configuration layers work

The AnduinOS package merges the following INI configuration files **key by key**, from lower to higher priority:

| Layer | File | Owner |
| --- | --- | --- |
| Vendor defaults | `/usr/share/anduinos-uresourced/defaults.conf` | Package; do not edit |
| Existing system configuration | `/etc/uresourced.conf` | Administrator; preserved for compatibility |
| System overrides | `/etc/uresourced.conf.d/*.conf`, in filename order | Administrator and Control Panel |
| Personal application preferences | `$XDG_CONFIG_HOME/uresourced.conf`, normally `~/.config/uresourced.conf` | User; only the `AppBoost` section applies |

Control Panel owns only `/etc/uresourced.conf.d/90-anduinos-control-panel.conf`. It is created when changes are saved. Administrator files such as `95-local.conf` sort later and take precedence. Deleting the Control Panel file exposes the lower layers; it does not remove administrator or personal overrides.

The machine-wide enable switch uses the AnduinOS-specific key:

```ini
[AnduinOS]
Enabled=false
```

Other keys retain their upstream names. For example, an administrator can create `/etc/uresourced.conf.d/95-local.conf`:

```ini
[ActiveUser]
MemoryMin=384M

[AppBoost]
ActiveCPUWeight=500
ActiveIOWeight=500
```

Apply manual edits with:

```bash
sudo /usr/lib/anduinos-uresourced/helper apply
```

The shared configuration reader validates values before the helper changes running services. Invalid configuration produces an error instead of silently applying guessed defaults. The helper restarts resource-management instances, not the desktop or terminal.

A personal file can override application weights, but cannot enable protection when the machine-wide switch is off or change other users' memory protection. Unlike unmodified upstream 0.5.5, this AnduinOS version merges personal `AppBoost` keys with system defaults instead of replacing the entire application configuration.

### Vendor defaults

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
DefaultCPUWeight=100
DefaultIOWeight=100
ActiveCPUWeight=300
ActiveIOWeight=300
BoostCPUWeightInc=200
BoostIOWeightInc=200
```

`SessionSlice` inherits the `ActiveUser` allocation unless explicitly overridden. CPU and I/O weights accept 1–10000; boost increments may be zero and must not bring the active weight above 10000. Memory values accept bytes, `K`, `M`, `G`, `T`, or a percentage of physical RAM. The GUI intentionally exposes fewer options.

The package migrates an unchanged old `/etc/uresourced.conf` into the vendor-default layer. A modified old file remains an administrator override. Package upgrades do not overwrite the Control Panel's saved choices.

Runtime cgroup properties and `/run/systemd/user/session.slice.d/99-uresourced.conf` are computed results, not another copy of user preferences. The services preserve the resource-property files they take over and restore them when stopping, including crash cleanup. They preserve properties changed externally after the daemon's last update.

## Restore or remove

Select **Restore Recommended Settings**, then **Apply**, to remove only the Control Panel override and apply the remaining configuration. Administrator and personal overrides remain effective and are reported in the window.

The command-line equivalent is:

```bash
sudo /usr/lib/anduinos-uresourced/helper reset
```

| Action | Result |
| --- | --- |
| Disable protection | Stop resource management and withdraw its runtime protection; retain tuning choices |
| Remove Control Panel | Retain backend configuration and operation |
| Remove `anduinos-uresourced` | Stop its instances and withdraw its runtime policy; retain saved choices for reinstalling |
| Purge `anduinos-uresourced` | Also remove its generated Control Panel configuration; retain administrator `95-local.conf` and personal files |

An old `/etc/uresourced.conf` that remains registered as an obsolete package conffile follows dpkg's normal purge rules. Keep a copy before purging if you need to preserve that legacy file. New administrator drop-ins are not packaged conffiles.

## Give heavy terminal jobs their own group

Run heavy work through `aos-bg`:

```bash
aos-bg make -j"$(nproc)"
```

It creates a unique scope under `background.slice` and passes command arguments unchanged. The interactive shell stays outside that job's OOM boundary. Appending `&` alone does not move work into a different resource group.

Memory-pressure termination works on a group of processes. A browser may be terminated as an entire application; this policy does not promise to select one browser tab. Keep unsaved work safe before deliberately testing memory exhaustion.

## Memory-pressure handling and feedback

The package's fixed `systemd-oomd` policy monitors user `app.slice` and `background.slice` for sustained memory pressure. The initial policy uses **80% memory pressure for 20 seconds**. This is time spent stalled, not the percentage of RAM in use.

The package cancels the broad root and `user@.service` monitoring supplied by the base policy. `session.slice` is outside the two monitored application trees. Administrator monitoring configured on other ancestors can still affect the scope, so inspect `oomctl` when diagnosing a customized system. System containers, virtual machines, and services need their own resource budgets; the kernel OOM handler remains the last resort.

The files belong to the backend package:

```text
/usr/lib/systemd/user/app.slice.d/30-anduinos-resource-policy.conf
/usr/lib/systemd/user/background.slice.d/30-anduinos-resource-policy.conf
/usr/lib/systemd/system/user@.service.d/30-anduinos-resource-policy.conf
/usr/lib/systemd/system/-.slice.d/30-anduinos-resource-policy.conf
```

Use administrator drop-ins under `/etc/systemd/` for custom systemd policy; do not edit the vendor files. These OOM settings are independent of the desktop-priority checkbox.

GNOME Settings Daemon watches user services and scopes for an `oom-kill` result and displays an application-stopped notification. It is the existing GNOME implementation, not an additional notification daemon. A `MemoryMax` limit can also cause this result, so the notification does not prove all physical memory was exhausted.

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

The helper's `status` command reads configuration and service state without administrator authentication. Inspect both the saved values and actual cgroup state when investigating a failed change.

For swap device configuration and its separate fallback layers, see [Swap Control Strategy](Swap-Control-Strategy.md).
