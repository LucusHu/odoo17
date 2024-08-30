import base64

from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES

from .ezpay_setting import *


class EzpayInvoice():
    TimeStamp = ''
    MerchantID = ''
    HashKey = ''
    HashIV = ''
    Send = 'Send'
    Invoice_Method = 'INVOICE'  # 電子發票執行項目
    Invoice_Url = 'Invoice_Url'  # 電子發票執行網址

    def __init__(self):
        self.Send = dict()
        # self.Send['MerchantID'] = ''
        # self.Send['HashKey'] = ''
        # self.Send['HashIV'] = ''
        self.Send['RespondType'] = 'JSON'  # 回應格式
        self.Send['Version'] = '1.5'  # 串接程式版本
        self.Send['TimeStamp'] = ''  # 時間戳記
        self.Send['MerchantOrderNo'] = ''  # 自訂編號
        self.Send['Status'] = '1'  # 開立發票方式 0 等待觸發開立 1 即時開立 3 預約自動開立
        self.Send['Category'] = 'B2B'
        self.Send['BuyerName'] = ''

        self.Send['BuyerEmail'] = ''
        self.Send['PrintFlag'] = ''
        self.Send['TaxType'] = ''
        self.Send['TaxRate'] = ''
        self.Send['Amt'] = ''
        self.Send['TaxAmt'] = ''
        self.Send['TotalAmt'] = ''
        self.Send['ItemName'] = ''
        self.Send['ItemCount'] = ''
        self.Send['ItemUnit'] = ''
        self.Send['ItemPrice'] = ''
        self.Send['ItemAmt'] = ''
        self.Send['Comment'] = ''
        self.Send['Currency'] = 'TWD'
        self.Send['ExchangeRate'] = '1'

    def Check_Out(self):
        arParameters = self.Send.copy()
        # arParameters['MerchantID_'] = self.MerchantID
        import time
        now_time = int(time.time())
        arParameters['TimeStamp'] = now_time
        arParameters['status'] = '1'
        return Ezpay_Invoice_Send.post_data_combine(arParameters, self.MerchantID, self.HashKey, self.HashIV,
                                                    self.Invoice_Url)


class EzpayInvoiceinvalid():
    TimeStamp = ''
    MerchantID = ''
    HashKey = ''
    HashIV = ''
    Send = 'Send'
    Invoice_Method = 'INVOICE'  # 電子發票執行項目
    Invoice_Url = 'Invoice_Url'  # 電子發票執行網址

    def __init__(self):
        self.Send = dict()
        self.Send['RespondType'] = 'JSON'  # 回應格式
        self.Send['Version'] = '1.0'  # 串接程式版本
        self.Send['TimeStamp'] = ''  # 時間戳記
        self.Send['InvoiceNumber'] = ''  # 發票號碼
        self.Send['InvalidReason'] = ''  # 作廢原因

    def do_invalid(self):
        arParameters = self.Send.copy()
        # arParameters['MerchantID_'] = self.MerchantID
        import time
        now_time = int(time.time())
        arParameters['TimeStamp'] = now_time
        arParameters['status'] = '1'
        return Ezpay_Invoice_Send.post_data_combine(arParameters, self.MerchantID, self.HashKey, self.HashIV,
                                                    self.Invoice_Url)


class Ezpay_Invoice_Send():
    # 發票物件
    InvoiceObj = ''
    InvoiceObj_Return = ''

    '''
    背景送出資料
    '''

    # CBC 加密
    def cbc_encrypt(self, plaintext, key, iv):
        """
        AES-CBC 加密
        key 必須是 16(AES-128)、24(AES-192) 或 32(AES-256) 位元組的 AES 金鑰；
        初始化向量 iv 為隨機的 16 位字串 (必須是16位)，
        解密需要用到這個相同的 iv，因此將它包含在密文的開頭。
        """
        # block_size = len(key)
        # padding = (block_size - len(plaintext) % block_size) or block_size  # 填充位元組
        #
        # mode = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode())
        # ciphertext = mode.encrypt((plaintext + padding * chr(padding)).encode())
        #
        # return base64.b64encode(iv.encode() + ciphertext).decode()
        # iv = reduce(lambda x, y: x + choice(digits + ascii_letters + punctuation), range(16), "")
        data = pad(plaintext.encode(), len(key))
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        print('random IV : ', base64.b64encode(cipher.iv).decode('utf-8'))
        data_check = cipher.encrypt(data)
        return data_check.hex()
        # return base64.b64encode(data_check), base64.b64encode(cipher.iv).decode('utf-8')

    # CBC 解密
    def cbc_decrypt(self, ciphertext, key):
        """
        AES-CBC 解密
        密文的前 16 個位元組為 iv
        """
        ciphertext = base64.b64decode(ciphertext)
        mode = AES.new(key.encode(), AES.MODE_CBC, ciphertext[:AES.block_size])
        plaintext = mode.decrypt(ciphertext[AES.block_size:]).decode()
        return plaintext[:-ord(plaintext[-1])]

    def post_data_combine(self, MerchantID, HashKey, HashIV, url):

        # url = 'https://cinv.ezpay.com.tw/Api/invoice_issue'
        headers = {"Content-Type": "application/json"}
        data = EzpayInvoice()
        sSend_Info = ''
        for key, val in self.items():
            if sSend_Info == '':
                sSend_Info += key + '=' + str(val)
            else:
                sSend_Info += '&' + key + '=' + str(val)
        # key = '4zRxZvzeuEW8RdfpHX6ILx2U3kSduxk7'
        # iv = 'CqBpI5quvPmjfPJP'
        key = HashKey
        iv = HashIV
        cipher = Ezpay_Invoice_Send.cbc_encrypt(self, sSend_Info, key, iv)
        transaction_data_array = {
            'MerchantID_': MerchantID,
            # 'MerchantID_': 34992198,
            'PostData_': cipher,
        }

        data_response = requests.post(url, transaction_data_array, timeout=120)
        return data_response
        # response = data_response.json()
