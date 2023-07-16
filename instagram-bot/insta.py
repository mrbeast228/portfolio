from random import randint
from uuid import uuid4
from time import time, sleep
from login import Login
from json import loads
from threading import Thread

def genDevId(seed):
    return "android-" + seed[:16]

def genUUID(minusesAllowed):
    generated = str(uuid4())
    if minusesAllowed:
        return generated
    else:
        return generated.replace("-", "")

def sendDm(user, pwd, recipient, message):
    randomUUID = genUUID(minusesAllowed=True)
    randDevId = genDevId(genUUID(minusesAllowed=False))

    headersToRequest = {
        "X-Pigeon-Rawclienttime": str(round(time() * 1000)),
        "X-IG-Bandwidth-Speed-KBPS": str(randint(7000, 10000)),
        "X-IG-Bandwidth-TotalBytes-B": str(randint(500000, 900000)),
        "X-IG-Bandwidth-TotalTime-MS": str(randint(50, 150)),
        "x-ig-app-startup-country": "AR",
        "x-bloks-version-id": "251c3023d7ef985a0e5d91b885c0c03bbb32b4b721d8de33bf9f667ba39b41ff",
        "x-ig-www-claim": "hmac.AR3ilHwjy8Cu_OTGprygpxuify0pDUKnrJvY1wRvzNSFRwwD",
        "x-bloks-is-layout-rtl": "false",
        "x-bloks-is-panorama-enabled": "true",
        "x-ig-device-id": randomUUID,
        "x-ig-family-device-id": "0ff91d16-df30-4b83-91bb-ef6fe5a751fa",
        "x-ig-android-id": randDevId,
        "x-ig-timezone-offset": "-7200",
        "x-ig-nav-chain": "1kw:feed_timeline:1,UserDetailFragment:profile:5,ProfileMediaTabFragment:profile:6,3xM:direct_thread:7",
        "x-ig-salt-ids": "1061163349",
        "x-ig-connection-type": "WIFI",
        "x-ig-capabilities": "3brTvx0=",
        "x-ig-app-id": "567067343352427",
        "priority": "u=3",
        "user-agent": "Instagram 207.0.0.39.120 Android (22/5.1.1; 240dpi; 720x1280; samsung; SM-G977N; beyond1q; shamu; es_ES; 321039156)",
        "accept-language": "es-ES, en-US",
        "x-mid": "YYMo4AALAAFf64y70slcLACzpklN",
        "ig-u-ig-direct-region-hint": "ATN,48835113737,1667518455:01f7b0ee46fcbbaff69dfacfa670268aabc23145ec3868c74813073fb68730959e36791f",
        "ig-u-shbid": "9315,48835113737,1667316351:01f7d3483a632756a67739318c409667f8bf628ab96357ac142d5f8d8b1aec633e00925d",
        "ig-u-shbt": "1635780351,48835113737,1667316351:01f71ee7fe18abe0f30183c1e9ee8bf2e11701e107f982cf35ad9f2095bf08e0b3d69414",
        "ig-u-rur": "VLL,48835113737,1667518478:01f7e869dc139eee715e5c5bfff4db350fe9c7f4c59979f70010e4333adbede244d9d068",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "accept-encoding": "zstd, gzip, deflate",
        "x-fb-http-engine": "Liger",
        "x-fb-client-ip": "True",
        "x-fb-server-cluster": "True"
    }

    loginSession = Login(user, pwd)
    loginResult = loginSession.login()
    if loginResult['success'] != 'ok':
        print("Login failed! Error content: ", loginResult['response'])
        return False

    idQuery = loginSession.session.get('https://www.instagram.com/web/search/topsearch/?query=' + recipient)
    recipientId = str(loads(idQuery.content)['users'][0]['user']['pk'])

    print("Login session created, starting posting...")
    textToSend = {
        "client_context": genUUID(minusesAllowed=True),
        "action": "send_item",
        "recipient_users": "[[" + recipientId + "]]",
        "text": message,
        "_uuid": randomUUID
    }
    for i in range(1):
        textToSend['text'] = str(i+1)
        t_worker = Thread(target=loginSession.session.post, kwargs=
                         {'url': 'https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/',
                          'headers': headersToRequest, 'data': textToSend})
        t_worker.start()
        sleep(0.1)
        print("Message " + str(i+1) + " sent")

    return True

sendDm('linuz0102', 'INSTA_PASSWORD', 'upos_tron', 'dick')
