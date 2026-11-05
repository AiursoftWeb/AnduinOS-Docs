# Tailscale

[Tailscale](https://tailscale.com/) connects your devices through an encrypted private network built on WireGuard. Your private Tailscale network is called a *tailnet*.

## Install from the official APT repository

Use Tailscale's Ubuntu repository matching the Ubuntu base of your AnduinOS installation. The current [one-command Linux installer](https://tailscale.com/install.sh) does not recognize `ID=anduinos`, so it can report that the distribution is unsupported even though the Ubuntu packages can be installed.

Open Terminal with `Ctrl + Alt + T`. Install the download tools first:

```bash
sudo apt update
sudo apt install ca-certificates curl
```

Then add the repository and install Tailscale:

```bash
(
    set -euo pipefail
    . /etc/os-release
    : "${UBUNTU_CODENAME:?Ubuntu base codename is missing; check /etc/os-release before continuing}"
    echo "Using Ubuntu codename: $UBUNTU_CODENAME"

    sudo mkdir -p --mode=0755 /usr/share/keyrings
    curl -fsSL "https://pkgs.tailscale.com/stable/ubuntu/${UBUNTU_CODENAME}.noarmor.gpg" \
      | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
    curl -fsSL "https://pkgs.tailscale.com/stable/ubuntu/${UBUNTU_CODENAME}.tailscale-keyring.list" \
      | sudo tee /etc/apt/sources.list.d/tailscale.list

    sudo apt update
    sudo apt install tailscale
    sudo systemctl enable --now tailscaled
)
```

The parentheses run these commands in a Bash subshell that stops if a command fails. `UBUNTU_CODENAME` selects the Ubuntu base, rather than treating the AnduinOS version number as an Ubuntu release. Do not default to `noble` when this field is missing, or replace it with another codename just to bypass a download error. Check the [official package instructions](https://pkgs.tailscale.com/stable/) for your base release instead.

This repository supplies updates through normal APT upgrades. Adding the repository does not itself enable unattended upgrades.

## Sign in and connect

Start Tailscale and follow the sign-in link printed in Terminal:

```bash
sudo tailscale up
```

Sign in with the account for your tailnet. If your organization requires device approval, wait for its administrator to approve this device.

Check the service and connection:

```bash
systemctl is-active tailscaled
tailscale status
tailscale ip -4
```

An active service means the daemon is running; it does not by itself mean that sign-in or device approval has finished. Once connected, `tailscale status` lists devices visible to you. To check another connected device, replace `my-other-device` with its Tailscale name or IP address:

```bash
tailscale ping my-other-device
```

For a temporary disconnection, run `sudo tailscale down`. To reconnect, run `sudo tailscale up`.

## Troubleshooting

- **The one-command installer reports an unsupported distribution:** use the APT instructions above; do not edit `/etc/os-release` to impersonate Ubuntu.
- **A repository download returns HTTP 404:** confirm `UBUNTU_CODENAME` in `/etc/os-release` and whether Tailscale publishes a repository for that Ubuntu release. Stop before installing if the repository files cannot be downloaded.
- **Cannot connect to the local daemon:** run `sudo systemctl enable --now tailscaled`, then inspect `systemctl status tailscaled` and `journalctl -u tailscaled -b` if it still fails.
- **The daemon runs but devices are unreachable:** check sign-in, device approval and your tailnet's access rules. See [Tailscale's Linux guide](https://tailscale.com/docs/install/linux).

## Remove Tailscale

Sign out before removing the package:

```bash
sudo tailscale logout
sudo apt remove tailscale
sudo rm -f /etc/apt/sources.list.d/tailscale.list
sudo rm -f /usr/share/keyrings/tailscale-archive-keyring.gpg
sudo apt update
```

Remove the device from the Tailscale admin console as well if you no longer want it registered in your tailnet.
