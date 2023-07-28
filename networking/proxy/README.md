# Mobile proxy proof-of-concept
This script allows your Android device to be a mobile proxy server using VPS server (white IP required)

## Requirments
+ mobile internet
+ Android 7.1+

## Installation and usage
1. Download proxy server application to your Android from Play Market - https://play.google.com/store/apps/details?id=cn.adonet.proxyevery
2. Setup proxy inside it:
   + IP address - 0.0.0.0
   + Port - 8080 (not to be confused with external port of VPS)
   + Enable basic authentication
   + Enter any username and password you want
3. Install Termux on your Android (from Play Market or APK)
4. Use `termux-change-repo` to switch Termux repository to Cloudflare
5. Run next commands in Termux:
   ```
   $ pkg install openssh wget openssl-tool sshpass tsu -y
   $ wget https://github.com/spbupos/projects-database/raw/main/networking/proxy/mobile_proxier.sh
   $ chmod 0755 mobile_proxier.sh
   $ ./mobile_proxier.sh ADDR PORT USERNAME PASSWORD
   ```
   where
   + `ADDR` - white IP of your VPS, it should have running SSH server
   + `PORT` - **EXTERNAL** port of your VPS, on which you will have your proxy opened
   + `USERNAME` and `PASSWORD` are credentials of SSH on your VPS, not to be confused with settings of proxy

   Script will went in background, and now you can connect to proxy to `ADDR:PORT` using username and password you set in step 2. IP address of your phone will become IP of your connected PC (for example)

## Tips
+ Script is looped and auto-reconnecting on failure (cooldown 15 s)
+ Script disables sleep of your device CPU, so it won't disconnect, but can discharge faster than usual
+ Mobile operators give our phones dynamic IPs, if you want to change it, you can enable and disable Airplane mode - mobile internet will be reconnected, proxy will be restarted automatically, and your IP will be changed
