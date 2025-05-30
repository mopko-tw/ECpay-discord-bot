import hashlib
import urllib.parse
from datetime import datetime, timedelta
import requests
import logging
import json
from config import ECPAY_CONFIG, ECPAY_TEST_URL, ECPAY_PROD_URL, USE_TEST_ENVIRONMENT

logger = logging.getLogger(__name__)

class ECPayHandler:
    def __init__(self):
        self.config = ECPAY_CONFIG
        self.api_url = ECPAY_TEST_URL if USE_TEST_ENVIRONMENT else ECPAY_PROD_URL
    
    def generate_check_mac_value(self, params):
        """產生檢查碼"""
        # 移除CheckMacValue參數
        if 'CheckMacValue' in params:
            del params['CheckMacValue']
        
        # 按照字母順序排序
        sorted_params = sorted(params.items())
        
        # 組合字串
        query_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
        
        # 加上HashKey和HashIV
        raw_string = f"HashKey={self.config['HashKey']}&{query_string}&HashIV={self.config['HashIV']}"
        
        # URL編碼
        encoded_string = urllib.parse.quote_plus(raw_string, safe='')
        
        # 轉小寫
        encoded_string = encoded_string.lower()
        
        # SHA256加密
        check_mac_value = hashlib.sha256(encoded_string.encode('utf-8')).hexdigest().upper()
        
        return check_mac_value
    
    def create_payment_form(self, trade_no, total_amount, trade_desc, item_name, store_type="ALL"):
        """建立付款表單"""
        # 計算到期日
        expire_date = (datetime.now() + timedelta(days=self.config['ExpireDate'])).strftime('%Y/%m/%d')
        create_time = datetime.now()
        expire_time = create_time + timedelta(days=self.config['ExpireDate'])
        
        # 基本參數
        params = {
            'MerchantID': self.config['MerchantID'],
            'MerchantTradeNo': trade_no,
            'MerchantTradeDate': create_time.strftime('%Y/%m/%d %H:%M:%S'),
            'PaymentType': self.config['PaymentType'],
            'TotalAmount': str(total_amount),
            'TradeDesc': trade_desc,
            'ItemName': item_name,
            'ReturnURL': self.config.get('PaymentInfoURL', ''),
            'ChoosePayment': self.config['ChoosePayment'],
            'EncryptType': str(self.config['EncryptType']),
            'ExpireDate': expire_date,
            'ClientRedirectURL': self.config.get('ClientRedirectURL', ''),
        }
        
        # 產生檢查碼
        params['CheckMacValue'] = self.generate_check_mac_value(params.copy())
        
        # 建立訂單資訊物件
        order_info = {
            'trade_no': trade_no,
            'total_amount': total_amount,
            'trade_desc': trade_desc,
            'item_name': item_name,
            'create_time': create_time,
            'expire_time': expire_time,
            'expire_date': expire_date,
            'merchant_id': self.config['MerchantID'],
            'store_type': store_type,
            'payment_code': self.generate_payment_code(trade_no, store_type),  # 根據超商類型生成代碼
            'ibon_code': self.generate_ibon_code(trade_no, total_amount),  # ibon機台專用代碼
            'barcode_1': self.generate_barcode_1(trade_no),
            'barcode_2': self.generate_barcode_2(trade_no),
            'barcode_3': self.generate_barcode_3(trade_no),
        }
        
        return params, order_info
    
    def generate_payment_code(self, trade_no, store_type="ALL"):
        """根據超商類型產生繳費代碼"""
        import random
        
        # 根據不同超商生成不同格式的代碼
        if store_type == "SEVEN":
            # 7-ELEVEN使用ibon代碼
            return self.generate_ibon_code(trade_no, 0)
        elif store_type == "FAMILY":
            # 全家便利商店代碼格式（通常12位數）
            prefix = "FM"
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            return prefix + suffix
        elif store_type == "HILIFE":
            # 萊爾富代碼格式（通常10位數）
            prefix = "HL"
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            return prefix + suffix
        elif store_type == "OK":
            # OK便利商店代碼格式（通常11位數）
            prefix = "OK"
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(9)])
            return prefix + suffix
        else:
            # 全通用代碼（一般格式）
            return f"{random.randint(10000, 99999)}{random.randint(10000, 99999)}"
    
    def generate_ibon_code(self, trade_no, amount):
        """產生ibon機台專用14位數繳費代碼"""
        # ibon機台繳費代碼格式：通常為14位數字
        # 格式：前2位為服務代碼 + 12位交易識別碼
        import random
        
        # 服務代碼（ECPay通常使用特定代碼）
        service_code = "88"  # ECPay在ibon的服務代碼
        
        # 生成12位交易識別碼（基於交易編號和金額）
        # 取交易編號的數字部分
        trade_digits = ''.join(filter(str.isdigit, trade_no))
        
        # 如果數字不足，用隨機數補足
        while len(trade_digits) < 12:
            trade_digits += str(random.randint(0, 9))
        
        # 取前12位
        transaction_id = trade_digits[:12]
        
        # 組合成14位ibon代碼
        ibon_code = service_code + transaction_id
        
        return ibon_code
    
    def generate_barcode_1(self, trade_no):
        """產生條碼1（模擬）"""
        import random
        return f"{random.randint(100000000000, 999999999999)}"
    
    def generate_barcode_2(self, trade_no):
        """產生條碼2（模擬）"""
        import random
        return f"{random.randint(100000000000, 999999999999)}"
    
    def generate_barcode_3(self, trade_no):
        """產生條碼3（模擬）"""
        import random
        return f"{random.randint(100000000000, 999999999999)}"
    
    def verify_callback(self, callback_data):
        """驗證回調資料"""
        try:
            # 取得回調的CheckMacValue
            received_check_mac = callback_data.get('CheckMacValue', '')
            
            # 重新計算CheckMacValue
            calculated_check_mac = self.generate_check_mac_value(callback_data.copy())
            
            # 比對檢查碼
            return received_check_mac.upper() == calculated_check_mac.upper()
        except Exception as e:
            logger.error(f"驗證回調資料時發生錯誤: {e}")
            return False
    
    def generate_payment_url(self, trade_no, total_amount, trade_desc, item_name, store_type="ALL"):
        """產生付款網址"""
        params, order_info = self.create_payment_form(trade_no, total_amount, trade_desc, item_name, store_type)
        
        # 建立表單HTML
        form_html = f"""
        <html>
        <head><meta charset="utf-8"></head>
        <body>
        <form id="ecpay_form" method="post" action="{self.api_url}">
        """
        
        for key, value in params.items():
            form_html += f'<input type="hidden" name="{key}" value="{value}">\n'
        
        form_html += """
        </form>
        <script>document.getElementById('ecpay_form').submit();</script>
        </body>
        </html>
        """
        
        return form_html, params, order_info
    
    def format_payment_info(self, order_info):
        """格式化付款資訊用於Discord Embed"""
        return {
            'payment_code': order_info['payment_code'],
            'ibon_code': order_info['ibon_code'],  # ibon代碼
            'trade_no': order_info['trade_no'],
            'item_name': order_info['item_name'],
            'total_amount': order_info['total_amount'],
            'create_time': order_info['create_time'].strftime('%Y/%m/%d %H:%M:%S'),
            'expire_time': order_info['expire_time'].strftime('%Y/%m/%d %H:%M:%S'),
            'expire_date': order_info['expire_date'],
            'merchant_id': order_info['merchant_id'],
            'store_type': order_info['store_type'],
            'barcode_1': order_info['barcode_1'],
            'barcode_2': order_info['barcode_2'],
            'barcode_3': order_info['barcode_3'],
        } 