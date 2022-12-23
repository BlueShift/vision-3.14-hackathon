# Panorama image creator

## Features
- Takes multiple pictures and merges them in one panoramic image

## Improvements
- Should be improved in the way that captures photos
- Can be improved to take 360 degrees photos

## Hardware requirements
- Raspberry PI
- 1 Camera required (usb or Pi)

### Tech
- Raspberry PI & Web camera
- OpenCV
- Python


### ArduCAM Driver
```bash
# Download the pivariety driver install script and make it executable
wget -O install_pivariety_pkgs.sh https://github.com/ArduCAM/Arducam-Pivariety-V4L2-Driver/releases/download/install_script/install_pivariety_pkgs.sh
chmod +x install_pivariety_pkgs.sh

# Install the Hawk-Eye kernel driver
./install_pivariety_pkgs.sh -p 64mp_pi_hawk_eye_kernel_driver
```

### Python
```python
pip install opencv-python
pip install Pillow
```