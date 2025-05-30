# ECPay Discord Bot v1.1.0

這是一個整合ECPay超商繳費功能的Discord Bot，讓使用者可以透過Discord指令建立超商繳費單。

## 🆕 v1.1.0 新功能

- 🖥️ **WebUI配置選項**: 可選擇使用本地WebUI或終端輸入配置
- 📋 **詳細繳費資訊**: Embed顯示完整訂單資訊（訂單ID、商品名稱、金額、時間等）
- 📁 **版本化文件**: README檔案版本化管理
- 💳 **繳費代碼顯示**: 直接在Discord中顯示繳費代碼

## 功能特色

- 🤖 **Slash Commands**: 使用現代化的Discord斜線指令
- 💳 **ECPay整合**: 支援超商代碼繳費（7-11、全家、萊爾富、OK）
- 🔐 **權限控制**: 可設定特定身分組才能使用指令
- 📊 **詳細記錄**: 完整的日誌記錄功能
- 🎨 **美觀介面**: 使用Discord Embed呈現資訊
- 🖥️ **靈活配置**: 支援WebUI或終端配置模式

## 安裝步驟

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 2. 配置設定

#### 方式一：使用WebUI配置（推薦）
1. 設定 `config.py` 中的 `USE_WEB_UI = True`
2. 執行 `python main.py`
3. 開啟瀏覽器訪問 `http://localhost:5000`
4. 在網頁介面中填入所有配置

#### 方式二：終端輸入配置
1. 設定 `config.py` 中的 `USE_WEB_UI = False`
2. 執行 `python main.py`
3. 按照提示在終端中輸入各項配置

#### 方式三：手動編輯配置檔案
編輯 `config.py` 檔案，填入以下資訊：

```python
# Discord Bot Token
DISCORD_BOT_TOKEN = "你的Discord Bot Token"

# 允許使用指令的身分組ID
ALLOWED_ROLE_IDS = [
    123456789012345678,  # 替換為實際的身分組ID
]

# ECPay設定
ECPAY_CONFIG = {
    "MerchantID": "你的商店代號",
    "HashKey": "你的HashKey", 
    "HashIV": "你的HashIV",
    # ... 其他設定
}
```

### 3. 建立Discord應用程式

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)
2. 建立新的應用程式
3. 在Bot頁面建立Bot並取得Token
4. 在OAuth2 > URL Generator中選擇：
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Use Slash Commands`, `Attach Files`

### 4. 取得身分組ID

1. 在Discord中開啟開發者模式（使用者設定 > 進階 > 開發者模式）
2. 右鍵點擊要授權的身分組
3. 選擇「複製ID」

### 5. ECPay設定

1. 註冊ECPay商家帳號
2. 取得測試環境的MerchantID、HashKey、HashIV
3. 設定付款完成通知網址（如果需要）

## 使用方法

### 啟動Bot

```bash
python main.py
```

### 可用指令

- `/create_payment` - 建立ECPay超商繳費單
  - `amount`: 金額（1-20000）
  - `description`: 交易說明
  - `item_name`: 商品名稱（可選）

- `/payment_status` - 查詢付款狀態
  - `trade_no`: 交易編號

- `/help_ecpay` - 顯示指令說明

## 繳費資訊顯示

Bot會在Discord中顯示完整的繳費資訊，包括：

- 💳 **繳費代碼**: 超商繳費專用代碼
- 🆔 **訂單ID**: 唯一交易識別碼
- 🛍️ **商品名稱**: 購買商品資訊
- 💰 **交易金額**: 應繳費金額
- ⏰ **訂單產生時間**: 建立時間
- ⏳ **訂單有效時間**: 繳費期限
- ❌ **訂單失效時間**: 過期時間

## 檔案結構

```
ecpay/
├── main.py              # 主程式檔案
├── config.py            # 配置設定
├── ecpay_handler.py     # ECPay處理模組
├── requirements.txt     # 依賴套件
├── readme/              # 文件資料夾
│   ├── README_v1.0.0.md # 舊版本文件
│   └── README_v1.1.0.md # 當前版本文件
└── bot.log             # 日誌檔案（執行後產生）
```

## 配置選項

### WebUI模式
- 提供友善的網頁介面
- 即時配置驗證
- 視覺化設定管理

### 終端模式
- 輕量化配置方式
- 適合伺服器環境
- 快速部署

## 注意事項

1. **測試環境**: 預設使用ECPay測試環境，正式使用前請修改 `config.py` 中的 `USE_TEST_ENVIRONMENT = False`

2. **權限設定**: 請確實設定 `ALLOWED_ROLE_IDS`，避免未授權使用者建立付款單

3. **金額限制**: 超商繳費有金額限制（1-20,000元）

4. **繳費期限**: 預設7天，可在config.py中調整

5. **安全性**: 
   - 不要將config.py上傳到公開的版本控制系統
   - 定期更換Bot Token和ECPay金鑰

6. **WebUI安全**: 
   - WebUI僅供本地配置使用
   - 配置完成後建議關閉WebUI模式

## 故障排除

### Bot無法啟動
- 檢查Discord Bot Token是否正確
- 確認已安裝所有依賴套件
- 檢查配置模式設定

### 指令無法使用
- 確認Bot有適當的權限
- 檢查身分組ID是否正確設定

### ECPay錯誤
- 驗證MerchantID、HashKey、HashIV是否正確
- 確認使用正確的環境（測試/正式）

### WebUI無法訪問
- 確認防火牆設定
- 檢查端口5000是否被占用

## 更新日誌

### v1.1.0 (2024-XX-XX)
- 新增WebUI配置選項
- 改進繳費資訊顯示
- 版本化README文件
- 優化使用者體驗

### v1.0.0 (2024-XX-XX)
- 初始版本發布
- 基本ECPay整合功能
- Discord Slash Commands支援

## 技術支援

如有問題請檢查 `bot.log` 日誌檔案，或聯繫開發者。

## 版本資訊

- 版本: 1.1.0
- Python: 3.8+
- Discord.py: 2.3.0+
- Flask: 2.3.0+ (WebUI模式) 