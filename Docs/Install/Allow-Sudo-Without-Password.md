# Allow sudo without a password

Passwordless sudo permits administrative commands without another password prompt. It does not make ordinary commands run as root, and it is separate from [automatic desktop login](./Accounts-and-Passwords.md). A process running under an account with unrestricted passwordless sudo can request full administrative access.

## Use the installer option when setting up a machine

The installer offers **Run sudo commands without a password**. Choose it only when the account should have that access. You must still set an account password during installation. Changing that password later does not remove an existing passwordless sudo rule.

## Configure an existing administrator account

Use `whoami` in your normal terminal to confirm the login name. In a separate terminal, run `sudo -i` and keep that root shell open for recovery until validation and testing succeed. An ordinary terminal with cached sudo authentication is not a reliable recovery shell if the policy becomes invalid. Back in your normal terminal, edit a dedicated file with syntax checking:

```bash
sudo visudo -f /etc/sudoers.d/local-passwordless
```

Add the following line, replacing `alice` with the intended login name:

```text
alice ALL=(ALL:ALL) NOPASSWD: ALL
```

Save and exit, then validate the complete policy:

```bash
sudo visudo -c
```

Fix any reported error before closing the root recovery shell; it can run `visudo -f /etc/sudoers.d/local-passwordless` without relying on sudo. In another terminal, `sudo -k` clears cached authentication, and `sudo -n true` tests whether the policy permits a command without prompting.

After validation and testing succeed, leave the recovery shell with `exit`.

## Restore password authentication

Set a usable account password first if the account has none. Remove the rule you added using `sudo visudo -f /etc/sudoers.d/local-passwordless`, then validate with `sudo visudo -c`. Existing installer-managed rules or other sudoers files can also grant passwordless access; inspect `sudo -l` rather than assuming removal of one rule changes all effective policy. Do not delete unrelated users' rules.

For authentication with a hardware key instead, see [Use YubiKey for sudo and login](../Skills/Secret-Management/Use-Yubikey-For-PAM-Auth.md).
