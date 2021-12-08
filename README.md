# dotfiles
These dotfiles are intended to be used on Arch or Arch based distributions, therefore every package link directs to an archlinux.org page and the installation commands use [pacman](https://archlinux.org/packages/core/x86_64/pacman/) and [yay](https://aur.archlinux.org/packages/yay/).


It goes without saying that AUR packages can be installed without yay or any other helper.

Everything can probably work in other distributions, but some of the software will need to be built from source because not packaged.
## **Package installation**
To install all the necessary packages use these two commands
```bash
pacman -S i3-gaps i3blocks i3status rofi dunst kitty feh curl sudo exa adobe-source-code-pro-fonts acpi iw sysstat ranger w3m ttf-droid
yay -S afetch cbonsai ttf-ms-fonts
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
## **Packages**
### **i3-gaps**
+ [i3-gaps](https://archlinux.org/packages/community/x86_64/i3-gaps/) [window manager]
+ [i3blocks](https://archlinux.org/packages/community/x86_64/i3blocks/) [i3bar output]
+ [i3status](https://archlinux.org/packages/community/x86_64/i3status/) [alternative i3bar output]
+ [kitty](https://archlinux.org/packages/community/x86_64/kitty/) [terminal emulator]
+ [rofi](https://archlinux.org/packages/community/x86_64/rofi/) [application launcher]
+ [feh](https://archlinux.org/packages/extra/x86_64/feh/) [wallpaper drawing]
### **i3blocks**
+ [curl](https://archlinux.org/packages/core/x86_64/curl/)
+ [ttf-ms-fonts](https://aur.archlinux.org/packages/ttf-ms-fonts/)
+ [dunst](https://archlinux.org/packages/community/x86_64/dunst/) [notification daemon]
### **Kitty**
+ [sudo](https://archlinux.org/packages/core/x86_64/sudo/)
+ [exa](https://archlinux.org/packages/community/x86_64/exa/) [ls replacement]
+ [ranger](https://archlinux.org/packages/community/any/ranger/) [TUI file manager]
+ [afetch](https://aur.archlinux.org/packages/afetch/) [minimal fetch script]
+ [cbonsai](https://aur.archlinux.org/packages/cbonsai/) [ASCII art bonsai drawing]
+ [adobe-source-code-pro-fonts](https://archlinux.org/packages/extra/any/adobe-source-code-pro-fonts/)
### **Ranger**
+ [w3m](https://archlinux.org/packages/extra/x86_64/w3m/) [used by ranger to display images in the terminal]
### **Battery script**
+ [acpi](https://archlinux.org/packages/community/x86_64/acpi/) [system information]
### **WiFi script**
+ [iw](https://archlinux.org/packages/core/x86_64/iw/) [wireless information and configuration]
### **CPU usage script**
+ [sysstat](https://archlinux.org/packages/community/x86_64/sysstat/) [system information]
### **Other**
+ [ttf-droid](https://archlinux.org/packages/community/any/ttf-droid/) [default VS Code font]
