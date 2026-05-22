# Allow sudo without password

Allowing sudo without password is a security risk, but it can be useful in certain situations.

!!! warning "Security Risk"

    Disabling the password requirement for sudo can be a security risk. This may cause some commands running without sudo to have root permissions and potentially break your system.

However, if you prefer to allow sudo without password, you can follow the steps below.

Open the sudoers file with the visudo command:

```bash title="Allow sudo without password"
sudo mkdir -p /etc/sudoers.d
sudo touch /etc/sudoers.d/$USER
echo "$USER ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers.d/$USER
```

That's it! You can now run sudo commands without entering your password.

## Suggested: Use YubiKey to authenticate sudo

Instead of completely disabling passwords (which is risky), you can configure Linux to accept a physical touch on your YubiKey as authentication. This offers **password-less convenience** with **hardware-level security**.

!!! warning "Replacing an old YubiKey?"

    U2F registration (for sudo/login) and SSH key generation (`ssh-keygen -t ecdsa-sk`) use **completely separate slots** on your YubiKey — they are independent registration paths. Replacing your key means you must re-register for both.

Run this script to install dependencies, register your key, and update the sudo configuration automatically.

```bash title="One-click Setup for Sudo with YubiKey"
# 1. Install necessary PAM module
sudo apt update
sudo apt install -y libpam-u2f

# 2. Register YubiKey
mkdir -p ~/.config/Yubico
if [ -s ~/.config/Yubico/u2f_keys ]; then
    echo "⚠️  Existing U2F registration found. Appending new key..."
    echo "   (To replace all keys, delete ~/.config/Yubico/u2f_keys first)"
fi
echo "👉 Please touch your YubiKey now to register it..."
pamu2fcfg --username="$(whoami)" >> ~/.config/Yubico/u2f_keys

# 3. Verify the connected key matches a registered one
CONNECTED=$(pamu2fcfg -n --username="$(whoami)" 2>/dev/null | awk -F: '{print $2}')
REGISTERED=$(cat ~/.config/Yubico/u2f_keys 2>/dev/null | awk -F: '{print $2}')

if [ -z "$CONNECTED" ]; then
    echo "❌ No YubiKey detected!"
elif echo "$REGISTERED" | grep -qF "$CONNECTED"; then
    echo "✅ Key verified — ready for sudo authentication"
else
    echo "❌ Connected key NOT found in u2f_keys! Registration may have failed."
fi

# 4. Configure PAM to allow YubiKey authentication
if grep -q "pam_u2f.so" /etc/pam.d/sudo; then
    echo "⚠️  Sudo PAM is already configured for YubiKey."
else
    # Backup original config
    sudo cp /etc/pam.d/sudo /etc/pam.d/sudo.bak

    # Insert the auth rule at line 2 (right after include common-auth)
    sudo sed -i '2i auth       sufficient   pam_u2f.so cue' /etc/pam.d/sudo
    echo "✅ PAM configured. Try running 'sudo -k' then 'sudo ls' to test."
fi
```

To learn more about how to use Yubikey to protect your SSH key, you can continue read more here: [Manage SSH Keys with Yubikey](../Skills/Secret-Management/Manage-SSH-Keys-with-Yubikey.md) guide to set up your YubiKey for SSH authentication.

You can also use YubiKey to auto unlock your LUKS encrypted disk at boot time. Check out the guide: [Auto Unlock LUKS with YubiKey](../Skills/Secret-Management/Use-Yubikey-To-Unlock-LUKS.md).

## Query which keys are trusted by your system

After setting up YubiKey authentication for sudo and login, you may want to verify which keys your system actually trusts. The following commands help you inspect the current state.

### List trusted U2F keys (sudo + GDM login)

U2F registrations for PAM-based authentication (sudo and GDM login) are stored in `~/.config/Yubico/u2f_keys`. Each line contains a username, a key handle, and a public key.

```bash title="View registered U2F key handles"
echo "=== Trusted U2F keys (sudo + GDM login) ==="
cat ~/.config/Yubico/u2f_keys 2>/dev/null | awk -F: '{print $2}' | tr ',' '\n' | grep -v 'es256\|presence'
```

### List trusted SSH keys

SSH keys stored on your YubiKey use a different slot and are managed through the SSH agent.

```bash title="View SSH keys in agent"
echo "=== Trusted SSH keys ==="
ssh-add -L 2>/dev/null | grep "sk-"
```

### Check which YubiKey is currently inserted

```bash title="List connected YubiKeys"
ykman list 2>/dev/null
```

### Cross-check: is the connected key trusted?

```bash title="Verify connected key against registered U2F keys"
CONNECTED=$(pamu2fcfg -n --username="$(whoami)" 2>/dev/null | awk -F: '{print $2}')
REGISTERED=$(cat ~/.config/Yubico/u2f_keys 2>/dev/null | awk -F: '{print $2}')

if [ -z "$CONNECTED" ]; then
    echo "No YubiKey detected"
elif echo "$REGISTERED" | grep -qF "$CONNECTED"; then
    echo "✅ Connected key IS trusted for login/sudo"
else
    echo "⚠️  Connected key is NOT registered."
    echo "   Run: pamu2fcfg --username=$(whoami) >> ~/.config/Yubico/u2f_keys"
fi
```
