# Desktop shortcuts, taskbar and wallpaper

These instructions apply to the AnduinOS GNOME desktop. Open **AnduinOS Appearance** from the application menu for the main desktop controls.

## Show or hide desktop icons

In **Panel Widgets**, toggle **Show Desktop Icons**. Files in your Desktop directory are shown when it is enabled. Use [text and icon sizing](./Text-Icons-and-Displays.md) to change their size; hiding icons does not delete their files.

## Put an application or website on the desktop

Use the application menu's pin-to-desktop action where available. Alternatively, copy the installed application's `.desktop` launcher into your Desktop directory. Its localized location can be found with `xdg-user-dir DESKTOP`. Use **Allow Launching** in the launcher's context menu if offered, but only for a launcher you trust.

For a website, use the browser's install-app or create-shortcut feature where available. A bookmark is an alternative when that browser has no desktop shortcut feature. See [Manage App Icons](../Skills/System-Management/Manage-App-Icons.md) for editing application launchers.

## Move the taskbar or start menu

Open **Taskbar Style** in AnduinOS Appearance. Select the Classic, Seperated or Centered layout and the desired screen edge. The available controls depend on the chosen layout. Use its **Advanced** page to reach extension preferences for more detailed panel controls. See the [Appearance guide](../Applications/System/AnduinOS-Appearance/AnduinOS-Appearance.md).

## Desktop wallpaper and login-screen wallpaper

Use **Settings → Appearance** to change the desktop background. Use **AnduinOS Appearance → GDM Wallpaper** for the sign-in screen; changing that shared screen requires administrator authentication. These are separate images.

For light/dark mode, select the desired appearance and reopen applications. Some Qt applications and websites maintain their own theme settings. If the taskbar disappears, follow [desktop troubleshooting](./Troubleshoot-Displays-and-Desktop.md) before attempting a factory reset.
