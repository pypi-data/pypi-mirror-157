from requests import post,get

class AsiaCell:

    def login(self,user):

        headers = {'Accept': '*/*',
            'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Length': '43',
            'content-type': 'application/json; charset=utf-8',
            'DeviceID': '9cddac0ba565c10576a6938fbbeda857',
            'Host': 'app.asiacell.com',
            'Origin': 'https://app.asiacell.com',
            'Referer': 'https://app.asiacell.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
        }

        r = post("https://app.asiacell.com/api/v1/login?lang=ar",headers=headers,json={"username":user,"captchaCode":""})

        PID = r.json()['nextUrl'].split("PID=")[1]

        return PID

    def smsvalidation(self, PID, password):
        tokh = {
            'Accept': '*/*',
            'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Length': '43',
            'content-type': 'application/json; charset=utf-8',
            'DeviceID': '9cddac0ba565c10576a6938fbbeda857',
            'Host': 'app.asiacell.com',
            'Origin': 'https://app.asiacell.com',
            'Referer': 'https://app.asiacell.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
        }

        tokg = post('https://app.asiacell.com/api/v1/smsvalidation?lang=ar',headers=tokh,json={"PID":PID,"passcode":password})

        return tokg.json()
    def home(self, access_token):
        headers_g = {
            'Accept': '*/*',
            'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
            'Authorization': 'Bearer '+access_token['access_token'],
            'Connection': 'keep-alive',
            'content-type': 'application/json; charset=utf-8',
            'DeviceID': '9cddac0ba565c10576a6938fbbeda857',
            'Host': 'app.asiacell.com',
            'Referer': 'https://app.asiacell.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
        r = get('https://app.asiacell.com/api/v1/home?lang=ar',headers=headers_g).json()

        return r