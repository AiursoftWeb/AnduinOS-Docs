# Secure Boot Signing Architecture

This document explains how AnduinOS handles Secure Boot module signing for third-party kernel drivers (NVIDIA, Xbox controller, IPU6 camera, etc.). It covers the full trust chain from UEFI firmware to kernel module, how Ubuntu provides the foundation, and what AnduinOS OOBE adds on top.

!!! note "For end users"
    If you just want to set up Secure Boot and install drivers, follow the [Secure Boot Guide](./First-Boot-For-Secure-Boot.md) and let the **Welcome Center** (OOBE) handle everything automatically. This document is for those who want to understand how it works under the hood.

---

## What Ubuntu Already Provides

The vast majority of the Secure Boot infrastructure is built by Ubuntu. AnduinOS stands on their shoulders:

| Component | Provided by | Role |
|-----------|------------|------|
| Shim (`shimx64.efi`) | Ubuntu / Microsoft-signed | Chain-loads GRUB, maintains MOK list |
| Kernel (`vmlinuz`) | Ubuntu / Canonical-signed | Trusted by Shim via Canonical's key |
| `update-secureboot-policy` | Ubuntu (`shim-signed`) | Generates MOK key pairs |
| Ubiquity `copy_mok()` | Ubuntu (installer) | Copies MOK keys to target system during installation |
| MOKManager blue screen | Shim | Firmware UI for enrolling keys at boot |
| DKMS framework | Ubuntu (`dkms`) | Builds and signs kernel modules from source |
| `ubuntu-drivers` | Ubuntu | Detects GPU, installs recommended driver |

**Ubuntu already does the heavy lifting.** During a fresh installation with "Install third-party software" checked, Ubiquity generates a MOK key, the installer's `copy_mok()` function copies it to the installed system, and the user enrolls it on first reboot via the MOKManager blue screen. After that, `ubuntu-drivers install` triggers DKMS to build and sign NVIDIA modules.

---

## The Full Trust Chain

Understanding why a click in the Welcome Center convinces the motherboard hardware to trust a third-party driver requires tracing the complete chain:

```text
┌─────────────────────────────────────────────────────────────────┐
│  UEFI Firmware (Motherboard)                                    │
│  Trusts: Microsoft Corporation UEFI CA                          │
│  "I only boot code signed by keys I know."                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  shimx64.efi (Shim)                                             │
│  Signed by: Microsoft → trusted by UEFI firmware               │
│  Role: Chain-loads GRUB, maintains the MOK List                │
│  "I trust binaries signed by Ubuntu AND keys the owner added." │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  GRUB → Linux Kernel (vmlinuz)                                  │
│  Signed by: Canonical Ltd. → trusted by Shim                   │
│  Kernel loads MOK keys into .machine → .secondary_trusted_keys │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Kernel Module (.ko) — e.g. hid-xpadneo.ko, nvidia.ko           │
│  Signed by: MOK.priv → checked against kernel keyring          │
│  If MOK enrolled and module signed with it → LOAD ✓            │
└─────────────────────────────────────────────────────────────────┘
```

---

## What AnduinOS OOBE Adds

Ubuntu's Secure Boot flow works perfectly in the ideal case. But when things go wrong — the user skipped the MOKManager blue screen, or a DKMS module was built before the signing config existed — Ubuntu offers terminal commands and Wiki pages. AnduinOS OOBE is a **graphical state inspector and recovery tool** that adds three things Ubuntu does not provide:

### 1. Five-layer health check

OOBE verifies every link in the chain, comparing what *should* be true against what *is* true:

```bash title="Five-layer health check"
mokutil --sb-state          → Is Secure Boot on?
mokutil --test-key          → Is MOK enrolled in firmware?
openssl x509 -serial        → What is the MOK certificate serial?
modinfo | grep sig_key      → What key actually signed the module?
String comparison           → Do the two serials match?
```

### 2. Explicit DKMS signing configuration

Ubuntu's DKMS (3.2.2+) can auto-detect MOK keys at `/var/lib/shim-signed/mok/MOK.priv`. However, in production testing, this fallback proved unreliable — modules were signed with a different auto-generated key despite the MOK key existing.

AnduinOS OOBE writes `/etc/dkms/framework.conf.d/anduinos-sb-sign.conf` to make the signing key explicit:

```ini
mok_signing_key="/var/lib/shim-signed/mok/MOK.priv"
mok_certificate="/var/lib/shim-signed/mok/MOK.der"
```

!!! note "No sign-file path needed"
    The config contains only key locations. DKMS automatically finds the correct `scripts/sign-file` binary for each kernel version. This survives kernel upgrades without maintenance.

### 3. One-click repair buttons

"Create & Enroll Certificate" and "Fix & Reinstall Driver" are GUI wrappers around Ubuntu's CLI tools. The underlying commands:

```bash
# Track A — Proactive: Secure Boot page
update-secureboot-policy --new-key  # Generate MOK key
mokutil --import MOK.der             # Queue for enrollment
cat > anduinos-sb-sign.conf          # Configure DKMS
dkms autoinstall                     # Rebuild & sign all modules

# Track B — Reactive: Xbox page Fix & Reinstall
cat > anduinos-sb-sign.conf          # Ensure DKMS config exists
apt reinstall -y anduinos-xbox-controller-driver  # Rebuild with correct key
```

---

## The OOBE State Machine

The Xbox controller page implements a three-row health check:

| Row | What | Green | Yellow | Red |
|-----|------|-------|--------|-----|
| R1 | Driver installed? | Installed | — | Not installed |
| R2 | Signature trusted? | Signed with current MOK | Signed but not enrolled / unknown cert | Not signed |
| R3 | Module status | Loaded / standing by | — | Blocked by Secure Boot |

### Button logic

| State | Button | Action |
|-------|--------|--------|
| Not installed + SB on + no MOK | Install (grayed) | Guide to Secure Boot page |
| Not installed + can install | Install (active) | Install driver package |
| Installed + signature mismatch | **Fix & Reinstall** | Write config → reinstall → refresh |
| Installed + all green | None | Pair/Test buttons visible |

---

## Why NVIDIA Also Benefits

The `anduinos-sb-sign.conf` is a **global DKMS configuration file.** It applies to every DKMS module on the system, not just the Xbox controller driver. When the user installs the NVIDIA proprietary driver, DKMS:

1. Reads `anduinos-sb-sign.conf`
2. Finds the MOK key paths
3. Signs `nvidia.ko`, `nvidia-modeset.ko`, etc. with the same MOK key
4. The kernel trusts these modules because the MOK certificate is already enrolled

No additional configuration, no per-driver scripts, no pink-screen debconf prompt. The signing infrastructure is in place from the moment the user goes through the Secure Boot page.

---

## Edge Cases

### Missed the Blue Screen

The user clicks "Create & Enroll Certificate," reboots, but MOKManager's 10-second timeout expires while they're making coffee.

**Response:** On next boot, OOBE re-checks `mokutil --test-key`. Key not enrolled → yellow warnings remain → repair button available. No infinite loop — just a state machine that reflects reality.

### Virtual Machines

Virtual machines expose incomplete or emulated Secure Boot. Xbox driver testing is meaningless inside a VM.

**Response:** `systemd-detect-virt` gates the Xbox page. In a VM, it never appears.

### No NVIDIA GPU

Machines without NVIDIA hardware should not see the driver page.

**Response:** `lspci` checks for "NVIDIA". If not found, the page is skipped.

### Secure Boot Disabled

If Secure Boot is off, the entire signing chain is irrelevant.

**Response:** The Secure Boot page is skipped. The Xbox page omits R2 (signature check). All green by default.

---

## Key Files

| File | Role |
|------|------|
| `/etc/dkms/framework.conf.d/anduinos-sb-sign.conf` | Global DKMS signing config (created by OOBE) |
| `/var/lib/shim-signed/mok/MOK.priv` | MOK private key |
| `/var/lib/shim-signed/mok/MOK.der` | MOK certificate (enrolled in UEFI firmware) |
| `/usr/sbin/update-secureboot-policy` | Ubuntu shim-signed tool |
| `/usr/bin/anduinos-oobe` | OOBE wizard (Secure Boot + Xbox pages) |

## Verification Commands

```bash
# Is Secure Boot on?
mokutil --sb-state

# Is the MOK certificate enrolled?
sudo mokutil --test-key /var/lib/shim-signed/mok/MOK.der

# Is DKMS configured to use the MOK key?
cat /etc/dkms/framework.conf.d/anduinos-sb-sign.conf

# What key signed the current module?
modinfo hid-xpadneo | grep -E "sig_key|signer"

# Compare with MOK certificate serial
openssl x509 -in /var/lib/shim-signed/mok/MOK.der -inform DER -noout -serial

# Does the module load?
sudo modprobe hid-xpadneo && lsmod | grep xpadneo
```

All three rows green in the OOBE Xbox page is the confirmation that the entire trust chain — UEFI → Shim → Kernel → DKMS → Module — is intact.
