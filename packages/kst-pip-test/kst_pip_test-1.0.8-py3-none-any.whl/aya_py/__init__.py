import requests
import base64
from Crypto.Cipher import AES


class MyClass:

    def __init__(self, key, secret, phone, password, decryptKey, production=False):
        self.__key = key
        self.__secret = secret
        self.__phone = phone
        self.__password = password
        self.__decryptKey = decryptKey
        if production:
            self.__prefix = ''.join(['/merchant', '/1.0.0'])
            self.__base = '.'.join(['api', 'ayapay', 'com'])
        else:
            self.__prefix = ''.join(['/om', '/1.0.0'])
            self.__base = '.'.join(['opensandbox', 'ayainnovation', 'com'])

    def __api(self, path, data, authorization):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        headers.update(authorization)
        r = requests.post('https://' + path, data=data, headers=headers)

        try:
            r.raise_for_status()

        except requests.exceptions.HTTPError as error:
            return 'Error ' + str(e)

        return r.json()

    def __unpad(s):
        return s[:-ord(s[len(s) - 1:])]

    def __getAccessToken(self):
        path = self.__base + '/token'

        data = {'grant_type': 'client_credentials'}

        eb = base64.b64encode(
            (self.__key + ':' + self.__secret).encode('utf-8'))
        es = str(eb, 'utf-8')
        authorization = {'Authorization': 'Basic ' + es}

        resp = self.__api(path, data, authorization)

        if 'access_token' in resp == False:
            return False

        self.__accesstoken = resp['access_token']
        return True

    def __getUserToken(self):
        at = self.__getAccessToken()
        if at == False:
            return False

        path = self.__base + self.__prefix + '/thirdparty/merchant/login'

        data = {'phone': self.__phone, 'password': self.__password}

        authorization = {'Token': 'Bearer ' + self.__accesstoken}

        resp = self.__api(path, data, authorization)

        if 'token' in resp == False or ('token' in resp and 'token' in resp['token'] == False):
            return False

        self.__usertoken = resp['token']['token']
        return True

    def createTransaction(self, customerPhone, amount, externalTransactionId, externalAdditionalData, v2=False, service='', timelimit=0):
        ut = self.__getUserToken()
        if ut == False:
            return False

        data = {
            'customerPhone': customerPhone,
            'amount': amount,
            'currency': 'MMK',
            'externalTransactionId': externalTransactionId,
            'externalAdditionalData': externalAdditionalData
        }

        if v2 == True:
            path = self.__base + self.__prefix + '/thirdparty/merchant/v2/requestPushPayment'

            if service == '':
                return 'service is required'

            data.update({'serviceCode': service})

            if timelimit != 0:
                data.update({'timelimit': timelimit})
        else:
            path = self.__base + self.__prefix + '/thirdparty/merchant/requestPushPayment'

        authorization = {
            'Token': 'Bearer ' + self.__accesstoken,
            'Authorization': 'Bearer ' + self.__usertoken
        }

        resp = self.__api(path, data, authorzation)
        return resp

    def createQR(self, amount, externalTransactionId, externalAdditionalData, v2=False, service='', timelimit=0):
        ut = self.__getUserToken()
        if ut == False:
            return False

        data = {
            'amount': amount,
            'currency': 'MMK',
            'externalTransactionId': externalTransactionId,
            'externalAdditionalData': externalAdditionalData
        }

        if v2 == True:
            path = self.__base + self.__prefix + '/thirdparty/merchant/v2/requestQRPayment'

            if service == '':
                return 'service is required'

            data.update({'serviceCode': service})

            if timelimit != 0:
                data.update({'timelimit': timelimit})
        else:
            path = self.__base + self.__prefix + '/thirdparty/merchant/requestQRPayment'

        authorization = {
            'Token': 'Bearer ' + self.__accesstoken,
            'Authorization': 'Bearer ' + self.__usertoken
        }

        resp = self.__api(path, data, authorzation)
        return resp

    def refundPayment(self, referenceNumber, externalTransactionId):
        ut = self.__getUserToken()
        if ut == False:
            return False

        path = self.__base + self.__prefix + '/thirdparty/merchant/refundPayment'

        data = {
            'referenceNumber': referenceNumber,
            'externalTransactionId': externalTransactionId
        }

        authorization = {
            'Token': 'Bearer ' + self.__accesstoken,
            'Authorization': 'Bearer ' + self.__usertoken
        }

        resp = self.__api(path, data, authorzation)
        return resp

    def decryptPayment(self, text):
        enc = base64.b64decode(text)
        cipher = AES.new(self.__key.encode(), AES.MODE_ECB)
        dtext = self.__unpad(cipher.decrypt(enc))
