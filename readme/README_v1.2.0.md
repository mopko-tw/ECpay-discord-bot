# ECPay Discord Bot v1.2.0

這是一個整合ECPay超商繳費功能的Discord Bot，讓使用者可以透過Discord指令建立超商繳費單。

## 🆕 v1.2.0 新功能

- 🇹🇼 **全中文指令**: 所有指令改為中文名稱（`/建立繳費單`、`/查詢付款狀態`、`/繳費說明`）
- 📁 **模塊化架構**: 指令系統重構為模塊化設計，方便擴展新功能
- 👁️ **公開顯示**: Embed訊息改為公開可見，方便團隊協作
- 🏪 **ibon機台支援**: 新增14位數ibon機台專用繳費代碼
- 📱 **詳細操作指南**: 提供ibon機台和其他超商的詳細繳費步驟

## 功能特色

- 🤖 **中文Slash Commands**: 使用繁體中文的Discord斜線指令
- 💳 **ECPay整合**: 支援超商代碼繳費（7-11、全家、萊爾富、OK）
- 🏪 **ibon機台專用**: 提供14位數專用代碼，適用於7-11 ibon機台
- 🔐 **權限控制**: 可設定特定身分組才能使用指令
- 📊 **詳細記錄**: 完整的日誌記錄功能
- 🎨 **美觀介面**: 使用Discord Embed呈現資訊
- 🖥️ **靈活配置**: 支援WebUI或終端配置模式
- 📁 **模塊化設計**: 指令系統模塊化，易於維護和擴展

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

- `/建立繳費單` - 建立ECPay超商繳費單
  - `金額`: 金額（1-20000）
  - `說明`: 交易說明
  - `商品名稱`: 商品名稱（可選）

- `/查詢付款狀態` - 查詢付款狀態
  - `交易編號`: 交易編號

- `/繳費說明` - 顯示指令說明

## 繳費資訊顯示

Bot會在Discord中顯示完整的繳費資訊，包括：

### ibon機台專用
- 🏪 **14位數ibon代碼**: 專用於7-11 ibon機台
- 📱 **詳細操作步驟**: 從機台操作到櫃台付款的完整流程

### 其他超商
- 🔢 **一般繳費代碼**: 適用於全家、萊爾富、OK便利商店
- 🏪 **櫃台繳費流程**: 直接向店員提供代碼繳費

### 訂單資訊
- 🆔 **訂單編號**: 唯一交易識別碼
- 🛍️ **商品名稱**: 購買商品資訊
- 💰 **交易金額**: 應繳費金額
- ⏰ **時間資訊**: 建立時間、有效期限、失效時間

## 檔案結構

```
ecpay/
├── main.py                    # 主程式檔案
├── config.py                  # 配置設定
├── ecpay_handler.py           # ECPay處理模組
├── requirements.txt           # 依賴套件
├── commands/                  # 指令模塊資料夾
│   ├── __init__.py           # 模塊初始化
│   └── payment_commands.py   # 付款相關指令
├── readme/                    # 文件資料夾
│   ├── README_v1.0.0.md      # v1.0.0版本文件
│   ├── README_v1.1.0.md      # v1.1.0版本文件
│   └── README_v1.2.0.md      # 當前版本文件
└── bot.log                   # 日誌檔案（執行後產生）
```

## ibon機台使用指南

### 操作步驟
1. 🏪 前往7-ELEVEN找到ibon機台
2. 📱 點選「儲值/繳費」
3. 💳 選擇「繳費」
4. 🔢 選擇「輸入代碼」
5. ⌨️ 輸入14位數繳費代碼
6. ✅ 確認金額後列印繳費單
7. 💰 持繳費單至櫃台付款

### 優勢特色
- ⏰ 24小時自助服務
- 🚀 快速便利操作
- 📄 自動列印繳費單
- 🔒 安全可靠

## 配置選項

### WebUI模式
- 提供友善的網頁介面
- 即時配置驗證
- 視覺化設定管理

### 終端模式
- 輕量化配置方式
- 適合伺服器環境
- 快速部署

### 模塊化架構
- 指令系統模塊化
- 易於添加新功能
- 代碼結構清晰

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

7. **ibon機台**: 
   - 14位數代碼專用於ibon機台
   - 其他超商請使用一般繳費代碼

## 故障排除

### Bot無法啟動
- 檢查Discord Bot Token是否正確
- 確認已安裝所有依賴套件
- 檢查配置模式設定

### 指令無法使用
- 確認Bot有適當的權限
- 檢查身分組ID是否正確設定
- 確認指令名稱使用中文

### ECPay錯誤
- 驗證MerchantID、HashKey、HashIV是否正確
- 確認使用正確的環境（測試/正式）

### WebUI無法訪問
- 確認防火牆設定
- 檢查端口5000是否被占用

### ibon機台問題
- 確認使用14位數ibon代碼
- 檢查代碼輸入是否正確
- 確認機台服務正常

## 更新日誌

### v1.2.0 (2024-XX-XX)
- 全中文指令系統
- 模塊化架構重構
- ibon機台專用代碼支援
- 公開顯示embed訊息
- 詳細操作指南

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

- 版本: 1.2.0
- Python: 3.8+
- Discord.py: 2.3.0+
- Flask: 2.3.0+ (WebUI模式) 