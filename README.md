# dotfiles
## Important information
### Disclaimer
Don't use if you don't know what you're doing.

### General
These dotfiles are intended to be used on Arch or Arch based distributions, therefore every package link directs to an archlinux.org page and the installation commands use [pacman](https://archlinux.org/packages/core/x86_64/pacman/) and [yay](https://aur.archlinux.org/packages/yay/).

It goes without saying that AUR packages can be installed without yay or any other helper.

Everything can probably work in other distributions too, but some of the software will need to be built from source because not packaged.
## **Package installation**
```bash
pacman -S xorg xorg-xinit rofi dunst alacritty feh curl sudo exa adobe-source-code-pro-fonts acpi iw sysstat ranger ueberzug ttf-droid bc polkit network-manager-applet noto-fonts wget python-requests gnome-keyring firefox gnome-themes-extra nemo lxappearance --needed
yay -S afetch cbonsai ttf-ms-fonts polkit-dumb-agent visual-studio-code-bin --needed
```
## **Setup**
Clone the repository in the home directory, `cd` into the setup directory and run the `setup.py` script

## **Packages**
### **General**
+ [xorg](https://archlinux.org/groups/x86_64/xorg/)
+ [xorg-xinit](https://archlinux.org/packages/extra/x86_64/xorg-xinit/)
+ [alacritty](https://archlinux.org/packages/community/x86_64/alacritty/) [terminal emulator]
+ [rofi](https://archlinux.org/packages/community/x86_64/rofi/) [application launcher]
+ [polkit](https://archlinux.org/packages/extra/x86_64/polkit/)
+ [polkit-dumb-agent](https://aur.archlinux.org/packages/polkit-dumb-agent-git/) [polkit agent]
+ [network-manager-applet](https://archlinux.org/packages/extra/x86_64/network-manager-applet/) [systray network utility]
+ [feh](https://archlinux.org/packages/extra/x86_64/feh/) [wallpaper drawing]
+ [curl](https://archlinux.org/packages/core/x86_64/curl/)
+ [dunst](https://archlinux.org/packages/community/x86_64/dunst/) [notification daemon]
+ [ttf-ms-fonts](https://aur.archlinux.org/packages/ttf-ms-fonts/)
+ [ttf-droid](https://archlinux.org/packages/community/any/ttf-droid/) [default VS Code font]
+ [noto-fonts](https://archlinux.org/packages/extra/any/noto-fonts/) [font for bar info]
+ [wget](https://archlinux.org/packages/extra/x86_64/wget/)
+ [gnome-keyring](https://archlinux.org/packages/extra/x86_64/gnome-keyring/)
+ [firefox](https://archlinux.org/packages/extra/x86_64/firefox/)
+ [visual-studio-code-bin](https://aur.archlinux.org/packages/visual-studio-code-bin)
+ [gnome-themes-extra](https://archlinux.org/packages/extra/x86_64/gnome-themes-extra/)
+ [nemo](https://archlinux.org/packages/community/x86_64/nemo/)
+ [lxappearance](https://archlinux.org/packages/community/x86_64/lxappearance/)
### **Alacritty**
+ [sudo](https://archlinux.org/packages/core/x86_64/sudo/)
+ [exa](https://archlinux.org/packages/community/x86_64/exa/) [ls replacement]
+ [ranger](https://archlinux.org/packages/community/any/ranger/) [TUI file manager]
+ [afetch](https://aur.archlinux.org/packages/afetch/) [minimal fetch script]
+ [cbonsai](https://aur.archlinux.org/packages/cbonsai/) [ASCII art bonsai drawing]
+ [adobe-source-code-pro-fonts](https://archlinux.org/packages/extra/any/adobe-source-code-pro-fonts/)
### **Ranger**
+ [ueberzug](https://archlinux.org/packages/community/x86_64/ueberzug/) [used by ranger to display images in the terminal]
### **Battery script**
+ [acpi](https://archlinux.org/packages/community/x86_64/acpi/) [system information]
### **WiFi script**
+ [iw](https://archlinux.org/packages/core/x86_64/iw/) [wireless information and configuration]
### **CPU usage script**
+ [sysstat](https://archlinux.org/packages/community/x86_64/sysstat/) [system information]
### **RAM usage script**
+ [bc](https://archlinux.org/packages/extra/x86_64/bc/) [floating point operations in shell scripts]
### **VPN/country script**
+ [python-requests](https://archlinux.org/packages/extra/any/python-requests/)
## **Color packages**
Color packages are a basic way to generalize the setup script for different color styles. They are JavaScript objects that (currently) contain four fields
+ mainColor
+ secondaryColor
+ wallpaperLink
+ wallpaperName

... all quite self explanatory names.

The values of the fields are then copied where appropriate in the configuration files, substituting their identifiers. The resulting configuration file is placed in a temporary folder and from there copied to the final destination.
