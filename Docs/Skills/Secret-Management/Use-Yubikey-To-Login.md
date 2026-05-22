# Use YubiKey To Login

If you want to enhance the security of your Linux desktop login, you can configure your system to use a YubiKey for authentication. This allows you to log in by simply touching your YubiKey, providing both convenience and strong security.

!!! warning "Replacing an old YubiKey?"

    U2F registration (for sudo/login) and SSH key generation (`ssh-keygen -t ecdsa-sk`) use **completely separate slots** on your YubiKey — they are independent registration paths. Replacing your key means you must re-register for both.

First, install the necessary PAM module and register your YubiKey.

```bash title="Step 1: Install libpam-u2f and register your YubiKey"
# Install necessary PAM module
sudo apt update
sudo apt install -y libpam-u2f

# Register YubiKey for U2F authentication
mkdir -p ~/.config/Yubico
if [ -s ~/.config/Yubico/u2f_keys ]; then
    echo "⚠️  Existing U2F registration found. Appending new key..."
    echo "   (To replace all keys, delete ~/.config/Yubico/u2f_keys first)"
fi
echo "👉 Please touch your YubiKey now to register it..."
pamu2fcfg --username="$(whoami)" >> ~/.config/Yubico/u2f_keys

# Verify the connected key matches a registered one
CONNECTED=$(pamu2fcfg -n --username="$(whoami)" 2>/dev/null | awk -F: '{print $2}')
REGISTERED=$(cat ~/.config/Yubico/u2f_keys 2>/dev/null | awk -F: '{print $2}')

if [ -z "$CONNECTED" ]; then
    echo "❌ No YubiKey detected!"
elif echo "$REGISTERED" | grep -qF "$CONNECTED"; then
    echo "✅ Key verified — ready for GDM login"
else
    echo "❌ Connected key NOT found in u2f_keys! Registration may have failed."
fi
```

Then configure GDM (GNOME Display Manager) to use your YubiKey for login authentication.

```bash title="Step 2: Configure GDM PAM for YubiKey"
# Define the target file (Ubuntu/Debian usually uses gdm-password)
TARGET="/etc/pam.d/gdm-password"

# Check if already configured
if grep -q "pam_u2f.so" "$TARGET"; then
    echo "⚠️  GDM PAM is already configured for YubiKey."
    echo "   (If you just registered a new key, you are all set.)"
else
    # Backup original config
    sudo cp "$TARGET" "$TARGET.bak"

    # Insert the auth rule at line 2 (Top priority)
    # This means: If key is touched, login immediately (skip password).
    sudo sed -i '2i auth       sufficient   pam_u2f.so cue' "$TARGET"
    echo "✅ PAM configured. Next time you login or unlock screen, just touch the Key."
fi
```

### What to expect at the lock screen

When you lock your screen or log out, you will see the password prompt as usual. If your YubiKey is plugged in, it will flash its LED — that is your signal to touch it. The **`cue` option does not display any on-screen message in the GDM graphical interface**, so watch for the blinking light on your key. If you do not touch the key within a few seconds, GDM falls back to the password prompt automatically.

!!! tip "Troubleshooting"

    If the YubiKey does not flash when you lock the screen, verify your key registration and PAM configuration by running the cross-check command in the [Query which keys are trusted](#query-which-keys-are-trusted) section below.

If anything goes wrong, press `Ctrl + Alt + F3` to switch to a terminal, log in with your username and password, and restore the original PAM configuration:

```bash title="Restore GDM PAM Configuration"
sudo mv /etc/pam.d/gdm-password.bak /etc/pam.d/gdm-password
```

This will revert the changes and allow you to log in with your password again.

## Use Yubikey to authenticate sudo commands

To use your YubiKey for authenticating `sudo` commands, you need to modify the PAM configuration for `sudo`. Read the instructions [here](../../Install/Allow-Sudo-Without-Password.md)

## Query which keys are trusted by your system

After setting up YubiKey authentication, you may want to verify which keys your system actually trusts. The following commands help you inspect the current state across both U2F (sudo/login) and SSH.

### List trusted U2F keys (sudo + GDM login)

U2F registrations for PAM-based authentication are stored in `~/.config/Yubico/u2f_keys`.

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
