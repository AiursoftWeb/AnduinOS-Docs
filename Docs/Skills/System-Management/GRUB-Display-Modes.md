# GRUB Display Modes

The GRUB screen appears before Linux starts, so its available resolutions come from the firmware and GRUB graphics drivers, not your desktop display settings. AnduinOS uses **Automatic** by default on both the Live ISO and an installed system. Automatic lets GRUB choose a supported mode; it does not promise the panel's native resolution.

After installation, open **Control Panel → Startup and Boot** to choose one of three modes:

| Mode | GRUB graphics setting | What to expect |
| --- | --- | --- |
| High resolution, if available | The connected display's preferred resolution, followed by `auto` | Sharper on supported firmware, but text may be very small on high-density displays. |
| Automatic (default) | `auto` | GRUB chooses a supported mode. This is the same default used by the Live ISO. |
| Large text | `1440x900,1280x800,1280x720,1024x768,auto` | Tries lower resolutions first; the final `auto` fallback keeps the menu usable if none are offered. |

These settings affect the **GRUB menu**, not the resolution of the desktop after Linux starts. The menu theme and its artwork are separate from the resolution choice.

## How the installed system is configured

`anduinos-grub-style` supplies `/etc/default/grub.d/20-anduinos-style.cfg`, which sets `GRUB_GFXMODE="auto"`. This package-owned file is the default. The Control Panel writes `/etc/default/grub.d/99-anduinos-control-panel.cfg` only when you save boot settings. GRUB reads the drop-ins in filename order, so the later `99-` file overrides the earlier `20-` default. A package update does not erase your Control Panel choice.

The Control Panel also saves the boot-menu timeout in its `99-` file and regenerates `/boot/grub/grub.cfg` by running `update-grub`. Do not edit that generated file directly. `GRUB_GFXPAYLOAD_LINUX="auto"` is a separate setting for the display mode handed to Linux; it does not force a GRUB menu resolution.

To inspect the source settings and the generated menu:

```bash
grep -H '^GRUB_GFXMODE=' /etc/default/grub /etc/default/grub.d/*.cfg 2>/dev/null
grep 'set gfxmode=' /boot/grub/grub.cfg
```

If a locally managed drop-in later than `99-anduinos-control-panel.cfg` also sets `GRUB_GFXMODE`, it can override the Control Panel. Remove or update that later setting before relying on the GUI again. For a safe reset, select **Automatic** in Control Panel; do not delete the whole `99-` file if it also contains your timeout choice.
