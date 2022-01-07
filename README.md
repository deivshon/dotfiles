# dotfiles
## Important information
### Disclaimer
These dotfiles were created for (my) personal use, and are therefore **NOT** tested on systems with different software/hardware configurations. I usually set them up after installing Arch on an otherwise nearly empty system. It is therefore important that, if you come across this repository and for some reason are interested in using it, know beforehand that it could cause your system to misbehave. It is important that you review the code that could cause said misbehaviour before trying to use it.

### General
These dotfiles are intended to be used on Arch or Arch based distributions, therefore every package link directs to an archlinux.org page and the installation commands use [pacman](https://archlinux.org/packages/core/x86_64/pacman/) and [yay](https://aur.archlinux.org/packages/yay/).

It goes without saying that AUR packages can be installed without yay or any other helper.

Everything can probably work in other distributions too, but some of the software will need to be built from source because not packaged.
## **Package installation**
To install all the necessary packages use these two commands
```bash
pacman -S i3-gaps i3blocks i3status rofi dunst kitty alacritty feh curl sudo exa adobe-source-code-pro-fonts acpi iw sysstat ranger ueberzug ttf-droid bc
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
+ [rofi](https://archlinux.org/packages/community/x86_64/rofi/) [application launcher]
+ [feh](https://archlinux.org/packages/extra/x86_64/feh/) [wallpaper drawing]
+ [curl](https://archlinux.org/packages/core/x86_64/curl/)
+ [ttf-ms-fonts](https://aur.archlinux.org/packages/ttf-ms-fonts/)
+ [dunst](https://archlinux.org/packages/community/x86_64/dunst/) [notification daemon]
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
### **Other**
+ [ttf-droid](https://archlinux.org/packages/community/any/ttf-droid/) [default VS Code font]
+ [kitty](https://archlinux.org/packages/community/x86_64/kitty/) [alternative terminal emulator]
+ [polkit-dumb-agent](https://aur.archlinux.org/packages/polkit-dumb-agent-git/) [polkit agent]
