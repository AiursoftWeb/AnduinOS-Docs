# Android apps, AMD compute, Windows domains and other desktops

These are compatibility questions, not promises that every third-party configuration is tested by AnduinOS. Check your OS version and hardware before following upstream instructions.

## Can I install Android APK files or Waydroid?

An APK is an Android application package; it is not a Linux `.deb` package or an AnduinOS Apkg project. The standard desktop does not run APK files directly. Waydroid is a separate Android-container project with its own kernel, graphics and session requirements. See [Waydroid installation requirements](https://docs.waydro.id/usage/install-on-desktops). Desktop Waydroid expects a Wayland session; app architecture, Google services and hardware access can impose additional limits. Its availability does not guarantee that a particular Android application will work.

## Does my AMD GPU support ROCm?

A GPU driving the desktop successfully does not establish ROCm compute compatibility. Match the exact GPU/APU, OS base, kernel and ROCm release against [AMD's compatibility guidance](https://www.amd.com/en/developer/resources/rocm-hub.html). Do not treat every Ubuntu-derived distribution or every Ryzen processor as validated. This documentation does not provide a tested AnduinOS ROCm installation procedure; keep compute-stack experiments separate from a working desktop where practical.

## Can I join a Windows Active Directory domain?

Accessing a [Windows file share](../Skills/File-System-Management/Mounting-Remote-Folder.md) is different from domain login. Domain membership can require organization-specific DNS, time synchronization, Kerberos and identity-service configuration. Coordinate with the domain administrator before enrolling the machine; obtain the supported client configuration, certificates and account policy. This documentation does not establish a tested AnduinOS-wide AD/LDAP deployment recipe. Keep a working local administrator account for recovery.

## Can I replace GNOME with KDE Plasma, Xfce or Cinnamon?

The AnduinOS desktop and its Appearance tools are built around GNOME and its extensions. Another desktop session may be installable from compatible repositories, but it will not automatically provide those integrations. Additional desktop packages can change login managers, themes and default applications. Test in a VM or separate installation first and preserve a working GNOME session. Do not remove the AnduinOS desktop packages just to try another session.

For changes within the supplied desktop, see [shortcuts and appearance](./Shortcuts-and-Appearance.md).
