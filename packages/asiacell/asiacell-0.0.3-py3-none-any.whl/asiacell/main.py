from requests import post,get

class AsiaCell:

    def login(self,user):

        headers = {
            'DeviceID': '8bfb8eabcf16425b78912b69918dcde3',
        }

        r = post("https://app.asiacell.com/api/v1/login?lang=ar",headers=headers,json={"username":user,"captchaCode":""})

        PID = r.json()['nextUrl'].split("PID=")[1]

        return PID

    def smsvalidation(self, PID, password):
        tokh = {
            'DeviceID': '8bfb8eabcf16425b78912b69918dcde3',
        }

        tokg = post('https://app.asiacell.com/api/v1/smsvalidation?lang=ar',headers=tokh,json={"PID":PID,"passcode":password})

        return tokg.json()
    def home(self, access_token):
        headers_g = {
            'Authorization': 'Bearer '+access_token['access_token'],
            'DeviceID': '8bfb8eabcf16425b78912b69918dcde3',
     }
        r = get('https://app.asiacell.com/api/v1/home?lang=ar',headers=headers_g).json()

        return r

    def profile(self, access_token):
        headers_g = {
            'Authorization': 'Bearer '+access_token['access_token'],
            'DeviceID': '8bfb8eabcf16425b78912b69918dcde3',
     }
        r = get('https://www.asiacell.com/api/v1/profile?lang=ar',headers=headers_g).json()

        return r

    def transformation(self, amount, member, access_token):
        tokh = {
            'Authorization': 'Bearer '+access_token['access_token'],
            'DeviceID': '8bfb8eabcf16425b78912b69918dcde3',
        }

        tokg = post('https://www.asiacell.com/api/v1/credit-transfer/start?lang=ar',headers=tokh,json={"amount":amount,"receiverMsisdn":member})

        return tokg.json()['PID']

    def donebg(self, PID, password, access_token):
        tokh = {
            'Authorization': 'Bearer '+access_token['access_token'],
            'DeviceID': '8bfb8eabcf16425b78912b69918dcde3',
        }

        tokg = post('https://www.asiacell.com/api/v1/credit-transfer/do-transfer?lang=ar',headers=tokh,json={"PID":PID,"passcode":password})

        return tokg.json()