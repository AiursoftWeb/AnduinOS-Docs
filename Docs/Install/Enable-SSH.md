# Enable SSH

By default, SSH is disabled (and not even installed) on AnduinOS. This is a deliberate "secure-by-default" design choice to ensure your system has zero open ports out of the box. 

However, if you are building a headless server or need to access your desktop remotely, you can easily enable it.

## Install the SSH Server

Since AnduinOS does not pre-install SSH, you must install the server package first. Open your terminal and run:

```bash title="Install SSH Server"
sudo apt update
sudo apt install openssh-server
```

## Connect

You can SSH to your machine using its IP address or hostname. To test it locally, run:

```bash title="Test SSH Locally"
ssh localhost
```

*(Note: If you are using the AnduinOS Firewall, remember to allow SSH connections before connecting remotely. See our [Firewall Guide](./Enable-Firewall.md) for details.)*
