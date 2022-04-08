# dotfiles
## Important information
### Disclaimer
Don't use if you don't know what you're doing.

### General
These dotfiles are intended to be used on Arch or Arch based distributions, therefore every package link directs to an archlinux.org page and the installation commands use [pacman](https://archlinux.org/packages/core/x86_64/pacman/) and [yay](https://aur.archlinux.org/packages/yay/).

It goes without saying that AUR packages can be installed without yay or any other helper.

Everything can probably work in other distributions too, but some of the software will need to be built from source because not packaged.
## **Package installation**
To install all the necessary packages use these two commands
```bash
pacman -S i3-gaps i3blocks i3status rofi dunst kitty alacritty feh curl sudo exa adobe-source-code-pro-fonts acpi iw sysstat ranger ueberzug ttf-droid bc polkit network-manager-applet noto-fonts
yay -S afetch cbonsai ttf-ms-fonts polkit-dumb-agent
```
## **Setup**
The dotfiles directory **must** be located in the home folder.

Run the following commands as a normal user, **not** as root.
```bash
cd
git clone https://github.com/deivshon/dotfiles
cd dotfiles/setup
./setup.py
```
### Important
The i3 configuration file contains a line that executes (if existing) the script located at ~/startup/startup.sh when i3 starts. This is needed by me to easily run small machine specific scripts at startup, but anyone who uses the configuration file should be aware of that.

The i3 configuration file also runs a feh command at startup and every i3 reload that draws the image located in ~/Pictures/wallpaper as the wallpaper.

## **Packages**
### **General**
+ [i3-gaps](https://archlinux.org/packages/community/x86_64/i3-gaps/) [window manager]
+ [i3blocks](https://archlinux.org/packages/community/x86_64/i3blocks/) [i3bar output]
+ [i3status](https://archlinux.org/packages/community/x86_64/i3status/) [alternative i3bar output]
+ [alacritty](https://archlinux.org/packages/community/x86_64/alacritty/) [terminal emulator]
+ [kitty](https://archlinux.org/packages/community/x86_64/kitty/) [alternative terminal emulator]
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

## **Color packages**
Color packages are a basic way to generalize the setup script for different color styles. They are JavaScript objects that (currently) contain three fields
+ mainColor
+ secondaryColor
+ wallpaperLink
+ wallpaperName

... all quite self explanatory names.

The values of the fields are then copied where appropriate in the configuration files, substituting their identifiers. The resulting configuration file is placed in a temporary folder and from there copied to the final destination.
