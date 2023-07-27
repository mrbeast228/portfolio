# Framebuffer updater
This tool force updates Linux framebuffer, what could be used for deploying desktop Linux on Android kernel (aka Halium)

## Motivation
If you will try to run X.Org on Android kernel using fbdev, you will see no errors in /var/log/Xorg.0.log, but your display will be black. This is ancient bug in Android kernel, this tool solves this issue

## Requirments
+ GCC (maybe for cross-compiling)
+ C standard library
+ C standard headers

## Building
```
gcc --static dfb2.c -o dfb2
```

## Usage
```
# ./dfb2 /dev/fb0 FPS
```
Here FPS usually is 60, but may be higher (sometimes it helps with permormance of framebuffer
