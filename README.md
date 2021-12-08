# dotfiles
## **Setup**
Run the following commands as a normal user, **not** as root.
```bash
cd ~
git clone https://github.com/deivshon/dotfiles
cd dotfiles/setup
./setup.py
```
## **Packages**
### **i3-gaps**
+ [i3-gaps](https://archlinux.org/packages/community/x86_64/i3-gaps/)
+ [i3blocks](https://archlinux.org/packages/community/x86_64/i3blocks/)
+ [i3status](https://archlinux.org/packages/community/x86_64/i3status/)
+ [kitty](https://archlinux.org/packages/community/x86_64/kitty/)
+ [rofi](https://archlinux.org/packages/community/x86_64/rofi/)
+ [feh](https://archlinux.org/packages/extra/x86_64/feh/)
### **i3blocks**
+ [curl](https://archlinux.org/packages/core/x86_64/curl/)
+ [ttf-ms-fonts](https://aur.archlinux.org/packages/ttf-ms-fonts/)
### **kitty**
+ [sudo](https://archlinux.org/packages/core/x86_64/sudo/)
+ [exa](https://archlinux.org/packages/community/x86_64/exa/)
+ [cbonsai](https://aur.archlinux.org/packages/cbonsai/)
+ [afetch](https://aur.archlinux.org/packages/afetch/)
+ [adobe-source-code-pro-fonts](https://archlinux.org/packages/extra/any/adobe-source-code-pro-fonts/)
### **Battery script**
+ [acpi](https://archlinux.org/packages/community/x86_64/acpi/)
### **WiFi script**
+ [iw](https://archlinux.org/packages/core/x86_64/iw/)
### **CPU usage script**
+ [sysstat](https://archlinux.org/packages/community/x86_64/sysstat/)
### **Other software for which config is present in this repository**
+ [ranger](https://archlinux.org/packages/community/any/ranger/)
## **Tweaking**
### **i3bar**
Install [ttf-ms-fonts](https://aur.archlinux.org/packages/ttf-ms-fonts/) to fix vertically misaligned text in i3bar

### **Visual Studio Code**
Install [ttf-droid](https://archlinux.org/packages/community/any/ttf-droid/) to get the default VS Code font

## **Package installation**
To install all the necessary packages use these two commands
```bash
pacman -S i3-gaps i3blocks i3status kitty feh curl sudo exa adobe-source-code-pro-fonts acpi iw sysstat ranger ttf-droid
yay -S afetch cbonsai ttf-ms-fonts
```
