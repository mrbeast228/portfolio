#!/bin/sh
exec 2>/dev/null

WHITE_IP_HOST="YOUR VPS ADDRESS HERE"
USERNAME="YOUR SERVER USERNAME"
PASSWORD="YOUR SERVER PASSWORD"
EXTERNAL_PROXY_PORT=$1

termux-wake-lock
while true; do
    sshpass -p $PASSWORD ssh -R $EXTERNAL_PROXY_PORT:127.0.0.1:8080 -N "$USERNAME"@"$WHITE_IP_HOST" -o StrictHostKeyChecking=no -o ExitOnForwardFailure=true
    sleep 16
done

exit 1
