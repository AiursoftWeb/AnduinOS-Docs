# GNOME desktop customization: extensions, taskbar and themes

AnduinOS is a configured GNOME desktop. Its taskbar, start menu, icons and theme integration already work together. Start with **AnduinOS Appearance** before adding extensions.

## Adjust the built-in desktop

1. Open **AnduinOS Appearance** from the application menu.
2. In **Taskbar Style**, choose Classic, Seperated or Centered and a screen edge. Change one setting at a time and check the result.
3. In **Panel Widgets**, enable or disable the optional widgets and Desktop Icons.
4. In **Advanced**, open the preferences of the existing extension when you need more detailed controls.

AnduinOS already supplies its customized **Dash to Panel**, along with ArcMenu and other desktop extensions. Installing another copy of Dash to Panel from an extension website can shadow the packaged copy and change its behavior. Configure the shipped version first. See the [Appearance reference](../Applications/System/AnduinOS-Appearance/AnduinOS-Appearance.md).

## Wallpaper scaling

Use **Settings → Appearance** to choose your desktop image. The sign-in screen has its own **GDM Wallpaper** page in AnduinOS Appearance.

If your image is cropped and you want to change how it fits, record the current desktop setting:

```bash
gsettings get org.gnome.desktop.background picture-options
```

List the supported choices:

```bash
gsettings range org.gnome.desktop.background picture-options
```

For example, fit the whole image while preserving its proportions:

```bash
gsettings set org.gnome.desktop.background picture-options 'scaled'
```

To undo, set the original value you recorded. `zoom` fills the screen and can crop edges; `spanned` uses an image across displays. This setting does not assign a different image to each monitor. Avoid installing a wallpaper extension until you have checked its compatibility with your GNOME Shell version.

## GNOME Tweaks and additional extensions

For controls outside AnduinOS Appearance, refresh APT metadata:

```bash
sudo apt update
```

Install the optional GNOME Tweaks application:

```bash
sudo apt install gnome-tweaks
```

Use Tweaks for the settings it exposes, such as fonts and legacy application themes. A GTK theme does not control every libadwaita, Qt or browser interface. AnduinOS also manages accent/theme synchronization, so verify custom choices after changing the system appearance.

To inspect extensions, use the installed **Extensions** application. If you specifically want an extension browser, the optional package is:

```bash
sudo apt install gnome-shell-extension-manager
```

Check the running Shell version before adding an extension:

```bash
gnome-shell --version
```

Add one compatible extension at a time. Avoid installing another implementation of a feature already active, especially taskbars, start menus and desktop icons. Keep track of which extension you added so you can disable it if a problem appears.

## Icons and a safe way back

For application launcher icons, use [Manage App Icons](../Skills/System-Management/Manage-App-Icons.md). For desktop icon size and display scaling, use [Text, Icons and Display Scaling](./Text-Icons-and-Displays.md). Custom icon themes need a proper theme directory, not a folder of unrelated PNG files; select a compatible installed theme in Tweaks instead of replacing files under `/usr/share/icons`.

If the panel disappears, disable the last extra extension and reopen AnduinOS Appearance to restore the intended layout. Save work, sign out and sign back in to reload GNOME Shell; `Alt+F2`, `r` is not a Wayland restart procedure. Avoid resetting the entire dconf database just to undo one setting. See [desktop troubleshooting](./Troubleshoot-Displays-and-Desktop.md) if the normal session remains unusable.
