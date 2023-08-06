from requests import post,get

class AsiaCell:

    def login(self,user, cap):

        headers = {
            'DeviceID': '6cf77389aa2b259c2951a12b3bad0175',
            }

        r1 = post("https://www.asiacell.com/api/v1/captcha?lang=ar",headers=headers,json={})
        img = r1.json()['captcha']['originSource']+r1.json()['captcha']['resourceUrl']

        cap = get(f"https://alshbg.ml/test/asiacell/cap.php?url={img}")

        r = post("https://www.asiacell.com/api/v1/loginV2?lang=ar",headers=headers,json={"username":user,"captchaCode":cap.text})

        PID = r.json()['nextUrl'].split("PID=")[1]

        return PID

    def smsvalidation(self, PID, password):
        tokh = {
            'DeviceID': '6cf77389aa2b259c2951a12b3bad0175',
        }

        tokg = post('https://app.asiacell.com/api/v1/smsvalidation?lang=ar',headers=tokh,json={"PID":PID,"passcode":password})

        return tokg.json()['access_token']
    def home(self, access_token):
        headers_g = {
            'Authorization': 'Bearer '+access_token,
            'DeviceID': '6cf77389aa2b259c2951a12b3bad0175',
     }
        r = get('https://app.asiacell.com/api/v1/home?lang=ar',headers=headers_g).json()

        return r

    def profile(self, access_token):
        headers_g = {
            'Authorization': 'Bearer '+access_token,
            'DeviceID': '6cf77389aa2b259c2951a12b3bad0175',
     }
        r = get('https://www.asiacell.com/api/v1/profile?lang=ar',headers=headers_g).json()

        return r

    def transformation(self, amount, member, access_token):
        tokh = {
            'Authorization': 'Bearer '+access_token,
            'DeviceID': '6cf77389aa2b259c2951a12b3bad0175',
        }

        tokg = post('https://www.asiacell.com/api/v1/credit-transfer/start?lang=ar',headers=tokh,json={"amount":amount,"receiverMsisdn":member})

        return tokg.json()['PID']

    def donebg(self, PID, password, access_token):
        tokh = {
            'Authorization': 'Bearer '+access_token,
            'DeviceID': '6cf77389aa2b259c2951a12b3bad0175',
        }

        tokg = post('https://www.asiacell.com/api/v1/credit-transfer/do-transfer?lang=ar',headers=tokh,json={"PID":PID,"passcode":password})

        return tokg.json()

    def recharge(self, resud):
        tokh = {
            'Authorization': 'Bearer '+access_token,
            'DeviceID': '6cf77389aa2b259c2951a12b3bad0175',
        }

        tokg = post('https://www.asiacell.com/api/v1/top-up?lang=ar',headers=tokh,json={"iccid":null,"voucher":resud,"msisdn":null,"rechargeType":1})

        return tokg.json()