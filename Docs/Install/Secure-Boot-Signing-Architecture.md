# The AnduinOS Boot Stack and Secure Boot Signing

AnduinOS 2.0.5 introduces an AnduinOS-maintained GRUB and a machine-local signing identity for new AMD64 installations on the Resolute base. The installation USB still starts through Ubuntu's officially signed bootloaders. These are two separate boot paths, not an inconsistent package database.

This page describes the package design and maintenance contract. For the blue enrollment screen, see the [Secure Boot Guide](./First-Boot-For-Secure-Boot.md); for graphical inspection and repair, use [Driver Center](../Applications/System/Driver-Center/Driver-Center.md).

!!! important "Existing users do not need to migrate"

    Normal updates within AnduinOS 2.0 do not require replacing Ubuntu's working bootloader or generating and enrolling a new certificate. Keep using the existing boot stack unless you deliberately choose a supported migration. Receiving 2.0.5 application updates is not a request to change firmware trust.

!!! warning "Do not independently upgrade to Ubuntu 26.10"

    Remaining on the Resolute base and installing its updates is different from a distribution upgrade. Do not use `do-release-upgrade` or change APT suites to move an existing AnduinOS installation to Ubuntu 26.10. Wait for an AnduinOS-supported upgrade procedure.

    Ubuntu reports that its 26.10 **signed GRUB** no longer reads Btrfs `/boot`. AnduinOS's default layout keeps `/boot` inside the Btrfs root filesystem, so replacing its bootloader with that build can make the system unbootable. This is a bootloader limitation, not removal of Btrfs from Linux. A separate ext4 `/boot` avoids this particular limitation, but does not make an untested distribution upgrade supported. See [Ubuntu's security announcement](https://ubuntu.com/blog/ubuntu-26-10-security).

## Scope and rationale

The new boot packages currently target **AMD64 on Resolute**. ARM64 retains its existing Ubuntu boot stack. Adapting the next Ubuntu base is separate work.

Keeping `/boot` with the Btrfs root filesystem allows the kernel and initramfs to stay with the system snapshot they belong to. Maintaining our GRUB build gives AnduinOS control over the filesystem and cryptographic readers needed for this layout, instead of changing the disk layout to match a reduced signed module set.

The build includes Btrfs, LUKS2, and Argon2 support. **These bootloader capabilities do not mean that disk-encryption installation or TPM automatic unlocking is delivered in 2.0.5.** Those require their own installer, recovery, and acceptance work.

AnduinOS keeps Ubuntu's officially signed shim and kernels. It does not ask users to replace the firmware's platform keys or trust an unsigned first-stage bootloader. In exchange for maintaining GRUB, the project must track GRUB security fixes, Ubuntu patches, shim compatibility, and SBAT/revocation changes.

## Packages and ownership

| Package | Responsibility |
|---|---|
| `anduinos-grub` | Builds GRUB with the Ubuntu patch set, BIOS/EFI tools, and an unsigned EFI template. The template is signed locally before deployment. No shared private key is shipped. |
| `anduinos-shim-signed` | Packages Ubuntu's already-signed shim and MokManager binaries, with AnduinOS dependency and deployment integration. The upstream EFI signatures are preserved. It depends on `anduinos-grub`. |
| `anduinos-secureboot-toolkit` | Inspects trust, manages the local certificate and DKMS configuration, and prepares, verifies, and deploys the locally signed GRUB. Driver Center and the installer share this implementation. |
| `anduinos-core-system` | Suggests `anduinos-shim-signed` on AMD64; it does not force an existing installation to replace its boot stack. |

The replacement packages declare the relevant **Provides**, **Conflicts**, and **Replaces** relationships. They replace the Ubuntu packages that own those bootloader files; they do not pretend that an Ubuntu package still owns an overwritten AnduinOS binary.

`Suggests` is intentionally weaker than `Depends` or `Recommends`. Default APT behavior does not install suggestions during an ordinary upgrade. Explicit installation or a custom policy that installs suggestions is a different operation. Fresh ISO construction explicitly selects the AnduinOS packages, so a fresh installed AMD64 system receives the new stack even though an existing system is not automatically migrated.

## One certificate, two signing mechanisms

```text
UEFI firmware
  → officially signed Ubuntu shim
      → locally MOK-signed AnduinOS GRUB
          → officially signed Ubuntu kernel
              → trusted kernel modules
```

The public certificate is enrolled in **shim's MOK trust store**, not normally in the motherboard's PK/KEK database. Driver Center's firmware-trust check reports this MOK enrollment.

The local identity can sign both EFI applications and kernel modules, but the signing tools and validators differ:

| Object | Signing and verification |
|---|---|
| AnduinOS GRUB EFI image | The toolkit uses `sbsign` and verifies the result before deployment. Shim validates it at boot. |
| Locally built DKMS modules, such as xpadneo | DKMS uses the kernel's `sign-file` mechanism with the configured local identity. The running kernel validates module signatures. |
| Official Ubuntu kernels and trusted prebuilt modules | Keep their upstream signatures; they do not need to be re-signed merely because the local MOK changes. |

GRUB is **not** a DKMS module. Sharing a certificate does not make its package hooks and the DKMS build hooks the same mechanism. Shim also does not directly validate drivers loaded later by Linux.

Older automatically generated certificates can carry the module-only extended-key-usage OID `1.3.6.1.4.1.2312.16.1.2`. Such a certificate can be useful for drivers while unsuitable for signing a GRUB that shim will accept. The new identity permits both purposes. This certificate permission is distinct from Unix file permissions on its private key.

## Why the Live USB still boots without your certificate

The ISO builder has two independent production paths:

```text
run_chroot_anduinos
  → installed-system packages, including AnduinOS GRUB/shim
  → kernel, initramfs, manifest, and squashfs

run_chroot_ubuntu
  → official bootloader packages selected from the target Ubuntu suite
  → extracted official EFI files for the ISO's removable-media boot path

build_iso
  → combines these outputs into the installation medium
```

The official bootloader packages are downloaded and extracted in the separate Ubuntu workspace. They are **not installed over the AnduinOS root filesystem**. The USB's firmware-facing EFI files can therefore boot before any local MOK exists, while the squashfs contains the AnduinOS package set and an unsigned GRUB template.

There is no temporary replacement package, no falsified dpkg database, and no machine's private signing key in the ISO. The installed boot stack and required payload are on the medium, so the installer can prepare the target without a network connection.

## Fresh installation and first boot

The installer:

1. Creates a new unified key pair in the target system. Independent installations get independent identities; retries of the same installation can reuse the verified target identity rather than generating another enrollment request.
2. Configures DKMS to use that identity for future local module builds.
3. Prepares and verifies a locally signed GRUB, then deploys the target boot files. The packaged source template remains unsigned.
4. Processes and checks relevant installed DKMS modules when applicable.
5. If Secure Boot is enabled, queues and verifies MOK enrollment before completing installation.

On the first restart, confirm **Enroll MOK → Continue → Yes**, enter `123456`, and reboot. This code authorizes the pending enrollment; it is not the disk-encryption password or the signing key's passphrase.

!!! warning "Enrollment is part of installation"

    With Secure Boot enabled, the new locally signed GRUB needs its certificate to be trusted. Skipping enrollment can prevent the installed system from booting, even though the Live USB still works. Do not apply the older advice that enrollment only affects optional drivers to this boot stack.

When Secure Boot is disabled, the installer still prepares the appropriate identity and locally signed GRUB, but does not automatically queue enrollment. Before enabling Secure Boot later, use Driver Center to complete certificate enrollment and check boot readiness. Turning on firmware enforcement first can lock the installed system out of its boot path.

## Existing installations and optional migration

An existing system can continue using Ubuntu's signed GRUB and its already-trusted driver certificates. A module-only certificate does not invalidate the official Ubuntu GRUB, which is trusted through Ubuntu's signing chain rather than that local certificate.

Consequently, a Driver Center finding such as **certificate cannot sign GRUB** or **AnduinOS GRUB not installed** is not, by itself, evidence that the old boot chain is broken. Existing users do not need to migrate merely to make the new-stack checks green.

For users who deliberately opt in, Driver Center separates certificate preparation/enrollment from bootloader replacement. A suitable certificate must be enrolled before replacing a working Secure Boot chain. Enrollment becomes usable without a separate manual **Use** step. Future signing uses the configured new identity; existing enrolled certificates are not automatically removed, and modules already trusted through them need not suddenly stop working.

The replacement workflow checks the APT plan, refuses unrelated removals, and preserves boot-file and firmware-entry recovery information. These safeguards are not a whole-disk backup or a guarantee against every power failure. Do not bypass the workflow with forced package removals or manual EFI overwrites.

## What happens when GRUB is updated or reinstalled?

The downloaded package contains an unsigned template, not the final machine-specific signed image:

```text
package configuration
  → validate the source template and signing identity
  → reuse a verified matching signed artifact, or sign a new candidate
  → verify the candidate signature
  → package trigger deploys the prepared boot chain
```

The preparation cache tracks the source image and certificate. Reinstalling identical inputs can reuse the existing artifact after verification; changed inputs require a newly signed artifact. Keeping the same enrolled certificate means an ordinary GRUB update does **not** require another MOK enrollment.

A signing failure must not deploy an unsigned replacement to the ESP. Deployment has its own backup and recovery handling. Package hooks may defer deployment when the installed boot configuration or mounted ESP is absent: package installation alone is therefore not proof that the machine's actual boot files are current.

`update-grub` regenerates the boot menu. It is not the EFI signing operation. Likewise, updating a kernel or DKMS driver does not mean rebuilding GRUB through DKMS.

## Inspection and repair

Start with **Driver Center → Secure Boot**. It separates firmware enforcement, local identity, certificate signing permissions, enrollment, module readiness, and the AnduinOS bootloader state. Follow the action associated with the failing check. Unknown or unreadable state must not be treated as Secure Boot being disabled.

Read-only command-line checks include:

```bash
anduinos-securebootctl status --json
mokutil --sb-state
mokutil --list-new
sudo mokutil --test-key /var/lib/shim-signed/mok/MOK.der
sudo dpkg --audit
dpkg-query -W anduinos-grub anduinos-shim-signed
```

Missing AnduinOS packages are expected on an unmigrated installation. A pending enrollment is not an enrolled certificate. A valid image signature alone does not prove that firmware selected that image or that shim's revocation policy accepts it: complete a real reboot as the final check.

The third-party-driver check concerns signing and trust, not whether a controller pairs correctly or a GPU application works. Test the actual hardware separately after changes.

### Files that matter

| Location | Purpose |
|---|---|
| `/usr/lib/anduinos-grub/grubx64.efi` | Package-owned unsigned EFI template; do not replace it with a locally signed copy. |
| `/var/lib/anduinos-grub/` | Generated signing/deployment state and recovery artifacts. |
| `/var/lib/shim-signed/mok/MOK.priv` | Machine-local private signing key. |
| `/var/lib/shim-signed/mok/MOK.der` | Public certificate used for MOK enrollment. |
| `/etc/dkms/framework.conf.d/anduinos-sb-sign.conf` | Persistent DKMS key selection. |
| The active ESP's AnduinOS EFI directory | Deployed shim, GRUB, and MokManager; discover the actual boot entry instead of assuming a directory name. |

Never publish the private key, copy it to another computer, or put it on the ESP. It is needed for future local signing. Restrictive file permissions protect against ordinary users, not an attacker who already controls root or can read an unencrypted disk offline. Machine-local signing is an explicit security trade-off, not equivalent to keeping a distribution's signing key offline.

## Maintainer checklist

* Track upstream GRUB security fixes and Ubuntu's patch set, and update pinned package-build inputs and their provenance deliberately.
* Preserve shim and MokManager's upstream signed bytes. Packaging them with different dependencies does not create a new Microsoft signature.
* Retain shim verification, the embedded readers required before `/boot` is accessible, and correct SBAT metadata. Never solve a boot failure by disabling signature enforcement.
* Keep the Live-media inputs separate from the installed-system package payload. Check both AMD64 and ARM64 media paths even where their installed boot stacks differ.
* Test offline UEFI/Secure Boot installation, physical MOK confirmation, removal of the installation medium, and a successful installed-system boot.
* Test ordinary upgrades of existing systems without forced migration, deliberate migration, same-version reinstall, changed-version re-signing, missing/untrusted keys, absent ESP, and interrupted deployment recovery.
* Verify trusted modules still work and untrusted boot images are rejected. A green status display or a successful package build alone is insufficient.

The 2.0.5 development validation includes an offline Secure Boot/Btrfs installation and enrollment test, a real-machine boot through the new chain, and a same-version GRUB reinstall that preserved a verified signed artifact and the active EFI files. These are useful regression cases, not substitutes for the complete release acceptance matrix or proof that disk-encryption installation is ready.

### Implementation references

* [ISO builder](https://github.com/AiursoftWeb/AnduinOS-2/blob/master/build.sh)
* [GRUB package](https://github.com/AiursoftWeb/AnduinOS-Packages/tree/master/anduinos-grub)
* [Shim package](https://github.com/AiursoftWeb/AnduinOS-Packages/tree/master/anduinos-shim-signed)
* [Shared Secure Boot toolkit](https://github.com/AiursoftWeb/AnduinOS-Packages/tree/master/anduinos-secureboot-toolkit)
* [Installer certificate preparation](https://github.com/AiursoftWeb/AnduinOS-Packages/blob/master/anduinos-installer-beta/src/installer_core/secure_boot.py)
