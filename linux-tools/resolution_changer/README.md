# Resolution add/change
This utility adds new screen modes to X.Org

## Requirments
+ xrandr
+ cvt

## Limitations
Modes are limited by resolution from above, it's property of your videocard. For example my mobile Intel Tiger-Lake Iris Xe graphics give black screen on modes bigger than 1440p

## Usage
```
$ ./x-resolution WIDTH HEIGHT [OUTPUT]
```
Output is defaulted to eDP-1 (laptop default), but you can have another. To get list of your outputs, run:
```
$ xrandr | grep connected
eDP-1 connected primary 2560x1440+0+0 (normal left inverted right x axis y axis) 309mm x 173mm
HDMI-1 disconnected (normal left inverted right x axis y axis)
```
In this example, we have connected eDP-1 and disconnected HDMI-1. Now you can run
```
$ ./x-resolution 1920 1080 eDP-1
```
Mode won't be changed automatically, but now you can set it in your DE settings
