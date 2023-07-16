from datetime import datetime
from re import search
from requests import Session
from json import loads

class Login:
    def __init__(self, user, pwd, enc_password=False):
        passwd = '#PWD_INSTAGRAM_BROWSER:0:<T>:' + pwd

        if passwd is not None:
            passwd = passwd.replace('<T>', str(int(datetime.now().timestamp())))
        else: raise Exception("Password error format!")

        self.auth = {
            "username": user,
            "enc_password": passwd,
        }
        self.login_url = "https://www.instagram.com/accounts/login/"
        self.login_url_ajax = self.login_url + "ajax/"

        self.session = None

    def response_parse(self, response):
        if response is not None:
            token = search('(csrf_token":")+(?P<value>[A-Za-z0-9]*)', response)
            token_value = token.groupdict()
            if token_value is not None:
                return {"success": "ok", "value": token_value.get("value")}
            return {"error": "Unable to extrack token from response!"}

    def _get_token(self):
        self.session = Session()
        self.session.headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 9; SM-A102U Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Instagram 155.0.0.37.107 Android (28/9; 320dpi; 720x1468; samsung; SM-A102U; a10e; exynos7885; en_US; 239490550)"

        get_token = self.session.get(self.login_url)

        if get_token.status_code == 200:
            self.status = 200
            headers = {}

            if get_token.cookies.get("csrftoken") is not None:
                headers["x-csrftoken"] = get_token.cookies["csrftoken"]
            else:
                csrf_token = self.response_parse(get_token.text)
                if csrf_token.get("success") != None:
                    headers["x-csrftoken"] = csrf_token.get("value")
                if csrf_token.get("error"):
                    return csrf_token
            return {
                'success': 'ok',
                'headers': headers,
                }
        return {'error': 'Error while getting response!'}

    def login(self):
        session_data = self._get_token()

        if session_data.get('success') == 'ok':
            headers = session_data.get("headers")
            log_in = self.session.post(self.login_url_ajax, data=self.auth, headers=headers)
            self.status = log_in.status_code
            if (str(loads(log_in.content)['status']) == 'ok'):
                return {'success': 'ok', 'response': log_in.content}
        return {'success': 'fail', 'response': log_in.content}
