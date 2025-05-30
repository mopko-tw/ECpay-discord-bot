# Discord Bot 配置範例
# 複製此檔案為 config.py 並填入實際的設定值

DISCORD_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"

# Bot擁有者ID（用於管理指令）
# 如何取得用戶ID：
# 1. 在Discord中開啟開發者模式（使用者設定 > 進階 > 開發者模式）
# 2. 右鍵點擊自己的用戶名 > 複製ID
BOT_OWNER_ID = 123456789012345678  # 替換為您的Discord用戶ID

# 是否使用WebUI配置介面
USE_WEB_UI = False  # True: 使用網頁配置, False: 使用終端輸入配置

# WebUI設定
WEB_UI_CONFIG = {
    "host": "127.0.0.1",  # WebUI主機位址
    "port": 5000,         # WebUI端口
    "debug": False        # 是否開啟除錯模式
}

# 允許使用指令的身分組ID列表
# 如何取得身分組ID：
# 1. 在Discord中開啟開發者模式（使用者設定 > 進階 > 開發者模式）
# 2. 右鍵點擊身分組 > 複製ID
ALLOWED_ROLE_IDS = [
    123456789012345678,  # 管理員身分組ID
    987654321098765432,  # 其他允許的身分組ID
]

# ECPay 配置
# 請至ECPay商家後台取得以下資訊
ECPAY_CONFIG = {
    "MerchantID": "YOUR_MERCHANT_ID_HERE",      # 商店代號
    "HashKey": "YOUR_HASH_KEY_HERE",           # HashKey
    "HashIV": "YOUR_HASH_IV_HERE",             # HashIV
    "PaymentType": "aio",                 # 付款方式
    "ChoosePayment": "CVS",               # 超商代碼繳費
    "EncryptType": 1,                     # 加密類型
    "ExpireDate": 7,                      # 繳費期限(天)
    "PaymentInfoURL": "https://your-domain.com/payment_info",  # 付款資訊接收網址
    "ClientRedirectURL": "https://your-domain.com/redirect",   # Client端返回網址
}

# ECPay 測試環境網址（請勿修改）
ECPAY_TEST_URL = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
# ECPay 正式環境網址（請勿修改）
ECPAY_PROD_URL = "https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5"

# 是否使用測試環境
# True: 測試環境（開發時使用）
# False: 正式環境（上線時使用）
USE_TEST_ENVIRONMENT = True

# 日誌設定
LOG_CONFIG = {
    "level": "INFO",                    # 日誌等級: DEBUG, INFO, WARNING, ERROR, CRITICAL
    "file": "bot.log",                  # 日誌檔案名稱
    "show_console": True,               # 是否在終端顯示日誌
    "show_backend": False,              # 是否顯示後端框架日誌（Discord.py, Flask等）
    "max_file_size": 10,                # 日誌檔案最大大小(MB)
    "backup_count": 5,                  # 保留的日誌備份檔案數量
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # 日誌格式
}

# 版本資訊
BOT_VERSION = "1.5.0" 