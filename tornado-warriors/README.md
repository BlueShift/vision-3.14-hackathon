# Team Tornado Warriors
## Photo booth camera

- 1-4 cameras taking photo for document 
- First challenge
  - Recognize from video stream if photo demands are met
- Second challenge
  - Crop and adjust the taken photo to meet demands

### Tech
- Raspberry PI & Ardu camera 
- OpenCV
- Python
- Pre-trained classifiers for face, eye and smile detection

### ArduCAM Driver
```
# Download the pivariety driver install script and make it executable
wget -O install_pivariety_pkgs.sh https://github.com/ArduCAM/Arducam-Pivariety-V4L2-Driver/releases/download/install_script/install_pivariety_pkgs.sh
chmod +x install_pivariety_pkgs.sh

# Install the Hawk-Eye kernel driver
./install_pivariety_pkgs.sh -p 64mp_pi_hawk_eye_kernel_driver
```
