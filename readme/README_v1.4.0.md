# ECPay Discord Bot v1.4.0

一個整合ECPay超商繳費功能的Discord機器人，支援全中文指令、多超商選擇和系統監控。

## 🆕 v1.4.0 新功能

### 📚 指令系統擴充
- **`/help`**：全新的幫助指令，顯示所有可用指令
- **`/機器人資訊`**：查看機器人詳細資訊和統計數據
- **動態權限顯示**：根據用戶權限動態顯示可用指令

### 🔧 管理功能
- **`/系統狀況`**：僅bot擁有者可用的系統監控指令
- **即時系統監控**：CPU、記憶體、磁碟、網路使用率
- **溫度監控**：支援硬體溫度顯示（如果可用）
- **程序監控**：Bot程序資源使用情況

### 👑 擁有者權限系統
- **BOT_OWNER_ID**：新增bot擁有者ID配置
- **權限分級**：一般用戶、身分組用戶、bot擁有者
- **安全控制**：管理指令僅限擁有者使用

## ✨ 主要功能

### 🎯 全中文指令系統
- `/建立繳費單` - 建立ECPay超商繳費單
- `/查詢付款狀態` - 查詢付款狀態  
- `/繳費說明` - 顯示繳費功能說明
- `/help` - 顯示所有指令說明
- `/機器人資訊` - 查看機器人詳細資訊
- `/系統狀況` - 查看系統狀況（僅擁有者）

### 🏪 超商選擇系統
- **🏪 全通用**：適用所有支援超商，顯示ibon代碼+一般代碼
- **🏪 7-ELEVEN**：專用ibon機台，14位數代碼
- **🏪 全家便利商店**：FM開頭12位數代碼
- **🏪 萊爾富**：HL開頭10位數代碼  
- **🏪 OK便利商店**：OK開頭11位數代碼

### 🔧 配置系統
- **WebUI模式**：網頁配置介面 (http://localhost:5000)
- **終端模式**：命令列互動配置
- **身分組權限**：支援多身分組權限控制
- **擁有者權限**：bot擁有者專用管理功能
- **測試/正式環境**：可切換ECPay環境

### 📊 系統監控
- **CPU監控**：使用率、核心數、邏輯核心
- **記憶體監控**：使用率、已使用、總容量
- **磁碟監控**：使用率、已使用、總容量
- **網路統計**：發送/接收流量、封包統計
- **程序監控**：Bot記憶體使用、CPU使用率
- **溫度監控**：硬體溫度顯示（支援的系統）
- **系統負載**：1/5/15分鐘平均負載（Unix/Linux）

### 📊 日誌管理
- **等級控制**：DEBUG/INFO/WARNING/ERROR/CRITICAL
- **顯示控制**：終端日誌、後端框架日誌開關
- **檔案管理**：輪轉日誌、大小限制、備份數量
- **格式自訂**：可自訂日誌輸出格式

## 🚀 快速開始

### 1. 環境需求
- Python 3.8+
- Discord Bot Token
- ECPay商家帳號

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 配置設定
複製 `config.example.py` 為 `config.py` 並修改配置：

```python
# Discord Bot 配置
DISCORD_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"

# Bot擁有者ID（用於管理指令）
BOT_OWNER_ID = 123456789012345678  # 替換為您的Discord用戶ID

# 是否使用WebUI配置介面
USE_WEB_UI = False  # True: 網頁配置, False: 終端配置

# 日誌設定
LOG_CONFIG = {
    "level": "INFO",                    # 日誌等級
    "file": "bot.log",                  # 日誌檔案
    "show_console": True,               # 終端顯示
    "show_backend": False,              # 後端框架日誌
    "max_file_size": 10,                # 檔案大小(MB)
    "backup_count": 5,                  # 備份數量
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# ECPay 配置
ECPAY_CONFIG = {
    "MerchantID": "YOUR_MERCHANT_ID_HERE",
    "HashKey": "YOUR_HASH_KEY_HERE", 
    "HashIV": "YOUR_HASH_IV_HERE",
    "ExpireDate": 7,  # 繳費期限(天)
}
```

### 4. 啟動機器人
```bash
python main.py
```

## 📋 指令說明

### 💳 繳費相關指令

#### `/建立繳費單`
建立ECPay超商繳費單

**參數：**
- `金額` (必填)：繳費金額 (1-20,000元)
- `說明` (必填)：交易說明
- `超商選擇` (必填)：選擇指定超商或全通用
- `商品名稱` (選填)：商品名稱，預設為"商品"

**超商選項：**
- 🏪 全通用（所有超商）
- 🏪 7-ELEVEN（ibon機台）
- 🏪 全家便利商店
- 🏪 萊爾富
- 🏪 OK便利商店

#### `/查詢付款狀態`
查詢指定交易的付款狀態

**參數：**
- `交易編號` (必填)：要查詢的交易編號

#### `/繳費說明`
顯示ECPay繳費功能的詳細說明

### ℹ️ 資訊指令

#### `/help`
顯示所有可用指令的說明，根據用戶權限動態顯示

#### `/機器人資訊`
查看機器人詳細資訊，包括：
- 基本資訊（名稱、ID、版本、運行時間）
- 統計資訊（伺服器數量、用戶數量、延遲）
- 系統資訊（Python版本、Discord.py版本、作業系統）
- ECPay設定（環境、商店代號、繳費期限）
- 功能狀態（各項功能啟用狀況）

### 🔧 管理指令（僅擁有者）

#### `/系統狀況`
查看伺服器系統狀況，僅bot擁有者可使用

**監控項目：**
- **CPU使用率**：即時CPU使用率、核心數
- **記憶體使用**：使用率、已使用/總容量
- **磁碟使用**：使用率、已使用/總容量
- **系統資訊**：作業系統、架構、運行時間
- **網路統計**：發送/接收流量、封包統計
- **Bot程序**：記憶體使用、虛擬記憶體、CPU使用率
- **溫度監控**：硬體溫度（如果支援）
- **系統負載**：1/5/15分鐘平均負載（Unix/Linux）

## 🏪 繳費流程

### 7-ELEVEN (ibon機台)
1. 前往7-ELEVEN找到ibon機台
2. 點選「儲值/繳費」→「繳費」→「輸入代碼」
3. 輸入14位數繳費代碼
4. 確認金額後列印繳費單
5. 持繳費單至櫃台付款

### 其他超商 (全家/萊爾富/OK)
1. 前往指定超商
2. 告知店員「代碼繳費」
3. 提供繳費代碼給店員
4. 確認金額後完成繳費
5. 保留收據作為憑證

## ⚙️ 配置選項

### Bot擁有者配置 (BOT_OWNER_ID)
```python
# 如何取得用戶ID：
# 1. 在Discord中開啟開發者模式（使用者設定 > 進階 > 開發者模式）
# 2. 右鍵點擊自己的用戶名 > 複製ID
BOT_OWNER_ID = 123456789012345678  # 替換為您的Discord用戶ID
```

### 日誌配置 (LOG_CONFIG)
```python
LOG_CONFIG = {
    "level": "INFO",                    # 日誌等級
    "file": "bot.log",                  # 日誌檔案名稱
    "show_console": True,               # 是否在終端顯示日誌
    "show_backend": False,              # 是否顯示後端框架日誌
    "max_file_size": 10,                # 日誌檔案最大大小(MB)
    "backup_count": 5,                  # 保留的日誌備份檔案數量
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}
```

**日誌等級說明：**
- `DEBUG`：詳細的除錯資訊
- `INFO`：一般資訊訊息
- `WARNING`：警告訊息
- `ERROR`：錯誤訊息
- `CRITICAL`：嚴重錯誤

**後端日誌控制：**
- `show_backend: False`：隱藏Discord.py、Flask等框架日誌
- `show_backend: True`：顯示所有框架日誌

### WebUI配置 (WEB_UI_CONFIG)
```python
WEB_UI_CONFIG = {
    "host": "127.0.0.1",    # 綁定IP
    "port": 5000,           # 埠號
    "debug": False          # 除錯模式
}
```

### ECPay配置 (ECPAY_CONFIG)
```python
ECPAY_CONFIG = {
    "MerchantID": "商店代號",
    "HashKey": "HashKey",
    "HashIV": "HashIV", 
    "ExpireDate": 7,        # 繳費期限(天)
}
```

## 🔒 權限設定

### 身分組權限
在 `ALLOWED_ROLE_IDS` 中設定允許使用繳費指令的Discord身分組ID：

```python
ALLOWED_ROLE_IDS = [
    123456789012345678,  # 管理員身分組
    987654321098765432,  # 其他身分組
]
```

### 擁有者權限
設定bot擁有者ID，擁有最高權限：

```python
BOT_OWNER_ID = 123456789012345678  # bot擁有者用戶ID
```

**權限等級：**
1. **一般用戶**：可使用 `/help`、`/機器人資訊`
2. **身分組用戶**：可使用所有繳費相關指令
3. **Bot擁有者**：可使用所有指令，包括 `/系統狀況`

## 📁 專案結構

```
ecpay/
├── main.py                 # 主程式
├── config.py              # 配置檔案
├── config.example.py      # 配置範例
├── ecpay_handler.py       # ECPay處理模組
├── requirements.txt       # 依賴套件
├── commands/              # 指令模塊
│   ├── __init__.py
│   └── payment_commands.py
├── readme/                # 文件資料夾
│   ├── README_v1.0.0.md
│   ├── README_v1.1.0.md
│   ├── README_v1.3.0.md
│   └── README_v1.4.0.md
└── bot.log               # 日誌檔案
```

## 🔧 故障排除

### 常見問題

1. **Bot無法啟動**
   - 檢查Discord Bot Token是否正確
   - 確認網路連線正常
   - 查看日誌檔案錯誤訊息

2. **指令無回應**
   - 確認身分組權限設定
   - 檢查Bot是否有適當的Discord權限
   - 查看日誌等級是否設為DEBUG以獲得更多資訊

3. **ECPay錯誤**
   - 驗證MerchantID、HashKey、HashIV設定
   - 確認測試/正式環境設定正確
   - 檢查金額是否在有效範圍內

4. **系統監控錯誤**
   - 確認已安裝psutil套件：`pip install psutil`
   - 檢查系統權限是否足夠
   - 某些監控功能可能在特定作業系統上不可用

5. **權限問題**
   - 確認BOT_OWNER_ID設定正確
   - 檢查用戶ID是否正確複製
   - 驗證身分組ID設定

### 日誌除錯

啟用DEBUG等級日誌以獲得詳細資訊：
```python
LOG_CONFIG = {
    "level": "DEBUG",
    "show_console": True,
    "show_backend": True,  # 顯示框架日誌
}
```

### 系統監控故障排除

1. **psutil相關錯誤**
   ```bash
   pip install --upgrade psutil
   ```

2. **溫度監控不可用**
   - Windows系統可能不支援溫度監控
   - 需要管理員權限或特定硬體支援

3. **系統負載不可用**
   - Windows系統不支援loadavg
   - 此功能僅在Unix/Linux系統上可用

## 📞 技術支援

如有問題請檢查：
1. 日誌檔案 (`bot.log`)
2. 配置檔案設定
3. Discord Bot權限
4. ECPay商家後台設定
5. 系統權限和依賴套件

## 📄 授權

此專案僅供學習和測試使用。

---

**ECPay Discord Bot v1.4.0** - 支援全中文指令、多超商選擇、進階日誌管理、系統監控 