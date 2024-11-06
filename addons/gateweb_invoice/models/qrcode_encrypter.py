from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import re


class QRCodeEncrypter:
    def __init__(self):
        # AES IV 固定值
        self.iv = base64.b64decode("Dt8lyToo17X/XkXaQvihuA==")

    def aes_encrypt(self, plain_text, aes_key):
        # 將文字轉為 bytes
        plain_bytes = plain_text.encode('utf-8')
        # 將 AESKey 轉為 bytes
        key_bytes = self.convert_hex_to_byte(aes_key)
        # 使用 AES 模式加密
        cipher = AES.new(key_bytes, AES.MODE_CBC, self.iv)
        # 將加密後的內容轉為 Base64 並返回
        encrypted_bytes = cipher.encrypt(pad(plain_bytes, AES.block_size))
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    def convert_hex_to_byte(self, hex_string):
        return bytes.fromhex(hex_string)

    def input_validate(self, invoice_number, invoice_date, invoice_time, random_number,
                       sales_amount, tax_amount, total_amount, buyer_identifier,
                       represent_identifier, seller_identifier, business_identifier,
                       product_array, aes_key):
        # 驗證 InvoiceNumber
        if not invoice_number or len(invoice_number) != 10:
            raise ValueError(f"Invalid InvoiceNumber: {invoice_number}")
        # 驗證 InvoiceDate
        if not invoice_date or len(invoice_date) != 7:
            raise ValueError(f"Invalid InvoiceDate: {invoice_date}")
        if not re.match(r"^\d{7}$", invoice_date):
            raise ValueError(f"Invalid InvoiceDate: {invoice_date}")
        year, month, day = int(invoice_date[:3]), int(invoice_date[3:5]), int(invoice_date[5:])
        if not (1 <= month <= 12 and 1 <= day <= 31):
            raise ValueError(f"Invalid InvoiceDate: {invoice_date}")
        # 驗證 InvoiceTime
        if not invoice_time or len(invoice_time) != 6:
            raise ValueError(f"Invalid InvoiceTime: {invoice_time}")
        # 驗證 RandomNumber
        if not random_number or len(random_number) != 4:
            raise ValueError(f"Invalid RandomNumber: {random_number}")
        # 驗證 SalesAmount, TaxAmount, TotalAmount
        if sales_amount < 0:
            raise ValueError(f"Invalid SalesAmount: {sales_amount}")
        if total_amount < 0:
            raise ValueError(f"Invalid TotalAmount: {total_amount}")
        # 驗證 BuyerIdentifier, RepresentIdentifier, SellerIdentifier, BusinessIdentifier
        if not buyer_identifier or len(buyer_identifier) != 8:
            raise ValueError(f"Invalid BuyerIdentifier: {buyer_identifier}")
        if not represent_identifier:
            raise ValueError(f"Invalid RepresentIdentifier: {represent_identifier}")
        if not seller_identifier or len(seller_identifier) != 8:
            raise ValueError(f"Invalid SellerIdentifier: {seller_identifier}")
        if not business_identifier:
            raise ValueError(f"Invalid BusinessIdentifier: {business_identifier}")
        # 驗證 ProductArray 和 AESKey
        if not product_array or len(product_array) == 0:
            raise ValueError("Invalid ProductArray")
        if not aes_key:
            raise ValueError("Invalid AESKey")

    def qr_code_inv(self, invoice_number, invoice_date, invoice_time, random_number,
                    sales_amount, tax_amount, total_amount, buyer_identifier,
                    represent_identifier, seller_identifier, business_identifier,
                    product_array, aes_key):
        # 檢查輸入參數
        self.input_validate(invoice_number, invoice_date, invoice_time, random_number,
                            sales_amount, tax_amount, total_amount, buyer_identifier,
                            represent_identifier, seller_identifier, business_identifier,
                            product_array, aes_key)

        # 組合發票訊息
        base_info = (invoice_number +
                     invoice_date +
                     random_number +
                     format(int(sales_amount), '08x') +
                     format(int(total_amount), '08x') +
                     buyer_identifier + seller_identifier)
        # 加密發票驗證文字
        encrypted_text = self.aes_encrypt(invoice_number + random_number, aes_key)

        return base_info + encrypted_text.ljust(24)
