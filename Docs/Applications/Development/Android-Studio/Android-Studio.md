# Android Studio and Android development

Android Studio is the IDE for building Android applications. This guide covers a native installation, an accelerated emulator, and USB debugging on AnduinOS.

## Check your computer

Open Terminal and check the architecture:

```bash
uname -m
```

These instructions target `x86_64` (AMD64). Google's current Linux requirements exclude ARM CPUs; AnduinOS supporting ARM64 does not make the Linux Android toolchain supported there. Check the [official installation requirements](https://developer.android.com/studio/install) before downloading.

Allow room for the IDE, SDK, Gradle caches and virtual devices. They grow independently. Keep projects in a normal Home folder and include them in an [independent backup](../../../Install/Backup-And-Restore.md).

## Install the native IDE

Download the Linux archive from [Android Studio](https://developer.android.com/studio). In Files, create `Applications` inside your Home folder and extract the archive there. The resulting directory should be `~/Applications/android-studio`; do not overwrite another installation.

Start its native launcher as your ordinary user:

```bash
"$HOME/Applications/android-studio/bin/studio"
```

Older archives may have `studio.sh` instead. Use the launcher shipped in your archive. Complete the setup wizard and install its SDK components. Use **Tools → Create Desktop Entry** to add a menu launcher.

In **SDK Manager**, note the Android SDK Location. The examples below use `~/Android/Sdk`; substitute the displayed location if different. Install the platform required by your project, Platform-Tools, and Android Emulator if needed.

Avoid mixing native and Flatpak installations while following this guide: their SDK locations and device access can differ. See [application sources](../../../Install/Installing-Applications.md).

## Enable emulator acceleration

Linux emulation uses KVM. Enable Intel VT-x or AMD-V in firmware if disabled, then inspect the device:

```bash
ls -l /dev/kvm
```

If the device exists but your user lacks access and its group is `kvm`, add yourself:

```bash
sudo usermod -aG kvm "$USER"
```

Sign out completely and sign in again. Run the SDK's check:

```bash
"$HOME/Android/Sdk/emulator/emulator" -accel-check
```

Expect a usable KVM result before creating an accelerated virtual device. A missing `/dev/kvm` needs virtualization/kernel investigation; changing file permissions to allow everyone does not fix missing virtualization. Inside a VM, the host must expose nested virtualization. See [Google's acceleration guide](https://developer.android.com/studio/run/emulator-acceleration).

Create a device in **Device Manager**, choose an appropriate system image and launch it. If only graphics rendering fails, try the emulator's software graphics option; that is separate from CPU acceleration.

## Connect an Android phone

Refresh package metadata:

```bash
sudo apt update
```

Install the Ubuntu-family USB rules package:

```bash
sudo apt install android-sdk-platform-tools-common
```

Add your user to the device-access group:

```bash
sudo usermod -aG plugdev "$USER"
```

Sign out and back in. Enable Developer options and USB debugging on the phone, connect a data-capable cable, unlock it, and approve your computer's debugging key. Check the connection with the SDK copy of ADB:

```bash
"$HOME/Android/Sdk/platform-tools/adb" devices
```

The phone should be listed as `device`. For `unauthorized`, check the phone's confirmation dialog. For no device, try another data cable/port and reconnect after installing the rules. Do not run ADB as root. See [hardware-device setup](https://developer.android.com/studio/run/device).

## Verify the complete setup

Create an **Empty Activity** project in Android Studio. Wait for Gradle synchronization, select your phone or emulator, and click **Run**. Success means the sample app opens on that device, not merely that the IDE starts.

For download failures, identify whether the failure is the SDK download or Gradle dependency resolution. Configure the corresponding tool's network settings; changing the AnduinOS APT mirror does not redirect either service. Use the IDE's update mechanism for this native archive installation and SDK Manager for SDK components.
