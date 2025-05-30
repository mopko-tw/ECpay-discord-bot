import discord
from discord.ext import commands
import logging
import asyncio
import threading
import getpass
from datetime import datetime
from logging.handlers import RotatingFileHandler

# 檢查是否需要WebUI
try:
    from config import USE_WEB_UI, WEB_UI_CONFIG
    if USE_WEB_UI:
        from flask import Flask, render_template_string, request, jsonify
        from flask_cors import CORS
except ImportError:
    USE_WEB_UI = False

from config import DISCORD_BOT_TOKEN, ALLOWED_ROLE_IDS, LOG_CONFIG, BOT_VERSION, BOT_OWNER_ID
from ecpay_handler import ECPayHandler

# 設定日誌系統
def setup_logging():
    """設定日誌系統"""
    # 清除現有的處理器
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # 設定根日誌等級
    logging.root.setLevel(getattr(logging, LOG_CONFIG['level']))
    
    # 建立格式器
    formatter = logging.Formatter(LOG_CONFIG['format'])
    
    # 設定處理器列表
    handlers = []
    
    # 檔案處理器（使用輪轉日誌）
    file_handler = RotatingFileHandler(
        LOG_CONFIG['file'], 
        maxBytes=LOG_CONFIG['max_file_size'] * 1024 * 1024,  # 轉換為位元組
        backupCount=LOG_CONFIG['backup_count'],
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)
    
    # 終端處理器（如果啟用）
    if LOG_CONFIG['show_console']:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
    
    # 設定應用程式日誌
    app_logger = logging.getLogger(__name__)
    app_logger.setLevel(getattr(logging, LOG_CONFIG['level']))
    for handler in handlers:
        app_logger.addHandler(handler)
    
    # 控制後端框架日誌
    if not LOG_CONFIG['show_backend']:
        # 設定Discord.py日誌等級
        logging.getLogger('discord').setLevel(logging.WARNING)
        logging.getLogger('discord.http').setLevel(logging.WARNING)
        logging.getLogger('discord.gateway').setLevel(logging.WARNING)
        logging.getLogger('discord.client').setLevel(logging.WARNING)
        
        # 設定Flask日誌等級
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('flask').setLevel(logging.WARNING)
        
        # 設定其他常見框架日誌
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
    else:
        # 如果要顯示後端日誌，設定為配置的等級
        backend_level = getattr(logging, LOG_CONFIG['level'])
        logging.getLogger('discord').setLevel(backend_level)
        logging.getLogger('werkzeug').setLevel(backend_level)
        logging.getLogger('flask').setLevel(backend_level)
        
        # 為後端日誌也添加處理器
        for logger_name in ['discord', 'werkzeug', 'flask']:
            backend_logger = logging.getLogger(logger_name)
            for handler in handlers:
                backend_logger.addHandler(handler)
    
    return app_logger

# 初始化日誌
logger = setup_logging()

# 全域配置變數
runtime_config = {}

def check_config_validity():
    """檢查配置是否有效"""
    required_fields = ['DISCORD_BOT_TOKEN', 'MerchantID', 'HashKey', 'HashIV']
    
    for field in required_fields:
        if field == 'DISCORD_BOT_TOKEN':
            if not runtime_config.get(field) or runtime_config[field] == "YOUR_DISCORD_BOT_TOKEN_HERE":
                return False, f"請設定 {field}"
        else:
            if not runtime_config.get('ECPAY_CONFIG', {}).get(field) or runtime_config['ECPAY_CONFIG'][field].startswith("YOUR_"):
                return False, f"請設定 ECPay {field}"
    
    return True, "配置有效"

def terminal_config():
    """終端配置模式"""
    print("=" * 60)
    print(f"🤖 ECPay Discord Bot v{BOT_VERSION} - 終端配置模式")
    print("=" * 60)
    
    # Discord Bot Token
    print("\n📱 Discord 設定")
    print("-" * 30)
    token = getpass.getpass("請輸入 Discord Bot Token: ").strip()
    runtime_config['DISCORD_BOT_TOKEN'] = token
    
    # 身分組ID
    print("\n請輸入允許使用指令的身分組ID（用逗號分隔，按Enter跳過使用預設值）:")
    role_ids_input = input("身分組ID: ").strip()
    if role_ids_input:
        try:
            role_ids = [int(id.strip()) for id in role_ids_input.split(',')]
            runtime_config['ALLOWED_ROLE_IDS'] = role_ids
        except ValueError:
            print("⚠️ 身分組ID格式錯誤，使用預設值")
            runtime_config['ALLOWED_ROLE_IDS'] = ALLOWED_ROLE_IDS
    else:
        runtime_config['ALLOWED_ROLE_IDS'] = ALLOWED_ROLE_IDS
    
    # ECPay設定
    print("\n💳 ECPay 設定")
    print("-" * 30)
    merchant_id = input("請輸入 MerchantID (商店代號): ").strip()
    hash_key = getpass.getpass("請輸入 HashKey: ").strip()
    hash_iv = getpass.getpass("請輸入 HashIV: ").strip()
    
    # 測試環境選擇
    print("\n🔧 環境設定")
    print("-" * 30)
    use_test = input("是否使用測試環境? (y/N): ").strip().lower()
    use_test_env = use_test in ['y', 'yes', '是']
    
    # 繳費期限
    expire_days_input = input("繳費期限（天數，預設7天）: ").strip()
    try:
        expire_days = int(expire_days_input) if expire_days_input else 7
    except ValueError:
        expire_days = 7
    
    runtime_config['ECPAY_CONFIG'] = {
        'MerchantID': merchant_id,
        'HashKey': hash_key,
        'HashIV': hash_iv,
        'PaymentType': 'aio',
        'ChoosePayment': 'CVS',
        'EncryptType': 1,
        'ExpireDate': expire_days,
        'PaymentInfoURL': '',
        'ClientRedirectURL': '',
    }
    
    runtime_config['USE_TEST_ENVIRONMENT'] = use_test_env
    
    print("\n✅ 配置完成！")
    print(f"🔧 測試環境: {'是' if use_test_env else '否'}")
    print(f"📅 繳費期限: {expire_days} 天")

def create_web_ui():
    """建立WebUI應用"""
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/')
    def index():
        return render_template_string(WEB_UI_TEMPLATE)
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        return jsonify({
            'discord_token': runtime_config.get('DISCORD_BOT_TOKEN', ''),
            'role_ids': ','.join(map(str, runtime_config.get('ALLOWED_ROLE_IDS', []))),
            'merchant_id': runtime_config.get('ECPAY_CONFIG', {}).get('MerchantID', ''),
            'hash_key': runtime_config.get('ECPAY_CONFIG', {}).get('HashKey', ''),
            'hash_iv': runtime_config.get('ECPAY_CONFIG', {}).get('HashIV', ''),
            'use_test_env': runtime_config.get('USE_TEST_ENVIRONMENT', True),
            'expire_days': runtime_config.get('ECPAY_CONFIG', {}).get('ExpireDate', 7)
        })
    
    @app.route('/api/config', methods=['POST'])
    def save_config():
        data = request.json
        
        try:
            runtime_config['DISCORD_BOT_TOKEN'] = data['discord_token']
            runtime_config['ALLOWED_ROLE_IDS'] = [int(id.strip()) for id in data['role_ids'].split(',') if id.strip()]
            runtime_config['USE_TEST_ENVIRONMENT'] = data['use_test_env']
            
            runtime_config['ECPAY_CONFIG'] = {
                'MerchantID': data['merchant_id'],
                'HashKey': data['hash_key'],
                'HashIV': data['hash_iv'],
                'PaymentType': 'aio',
                'ChoosePayment': 'CVS',
                'EncryptType': 1,
                'ExpireDate': int(data['expire_days']),
                'PaymentInfoURL': '',
                'ClientRedirectURL': '',
            }
            
            return jsonify({'success': True, 'message': '配置已儲存'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'配置錯誤: {str(e)}'})
    
    return app

# WebUI HTML模板
WEB_UI_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECPay Discord Bot 配置</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
        button { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .alert { padding: 15px; margin: 20px 0; border-radius: 5px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .section { margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
        .section h3 { margin-top: 0; color: #495057; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 ECPay Discord Bot 配置</h1>
        
        <div id="alert" style="display: none;"></div>
        
        <form id="configForm">
            <div class="section">
                <h3>📱 Discord 設定</h3>
                <div class="form-group">
                    <label for="discord_token">Discord Bot Token:</label>
                    <input type="password" id="discord_token" name="discord_token" required>
                </div>
                <div class="form-group">
                    <label for="role_ids">允許使用的身分組ID (用逗號分隔):</label>
                    <input type="text" id="role_ids" name="role_ids" placeholder="123456789012345678,987654321098765432">
                </div>
            </div>
            
            <div class="section">
                <h3>💳 ECPay 設定</h3>
                <div class="form-group">
                    <label for="merchant_id">MerchantID (商店代號):</label>
                    <input type="text" id="merchant_id" name="merchant_id" required>
                </div>
                <div class="form-group">
                    <label for="hash_key">HashKey:</label>
                    <input type="password" id="hash_key" name="hash_key" required>
                </div>
                <div class="form-group">
                    <label for="hash_iv">HashIV:</label>
                    <input type="password" id="hash_iv" name="hash_iv" required>
                </div>
            </div>
            
            <div class="section">
                <h3>🔧 其他設定</h3>
                <div class="form-group">
                    <label for="use_test_env">使用測試環境:</label>
                    <select id="use_test_env" name="use_test_env">
                        <option value="true">是 (測試環境)</option>
                        <option value="false">否 (正式環境)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="expire_days">繳費期限 (天):</label>
                    <input type="number" id="expire_days" name="expire_days" value="7" min="1" max="30">
                </div>
            </div>
            
            <button type="submit">💾 儲存配置並啟動Bot</button>
        </form>
    </div>

    <script>
        // 載入現有配置
        fetch('/api/config')
            .then(response => response.json())
            .then(data => {
                document.getElementById('discord_token').value = data.discord_token;
                document.getElementById('role_ids').value = data.role_ids;
                document.getElementById('merchant_id').value = data.merchant_id;
                document.getElementById('hash_key').value = data.hash_key;
                document.getElementById('hash_iv').value = data.hash_iv;
                document.getElementById('use_test_env').value = data.use_test_env.toString();
                document.getElementById('expire_days').value = data.expire_days;
            });

        // 提交表單
        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                discord_token: formData.get('discord_token'),
                role_ids: formData.get('role_ids'),
                merchant_id: formData.get('merchant_id'),
                hash_key: formData.get('hash_key'),
                hash_iv: formData.get('hash_iv'),
                use_test_env: formData.get('use_test_env') === 'true',
                expire_days: formData.get('expire_days')
            };
            
            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                const alert = document.getElementById('alert');
                if (result.success) {
                    alert.className = 'alert alert-success';
                    alert.textContent = '✅ ' + result.message + ' - Bot將在幾秒後啟動...';
                    alert.style.display = 'block';
                    setTimeout(() => {
                        window.close();
                    }, 3000);
                } else {
                    alert.className = 'alert alert-error';
                    alert.textContent = '❌ ' + result.message;
                    alert.style.display = 'block';
                }
            });
        });
    </script>
</body>
</html>
'''

# 設定Discord intents
intents = discord.Intents.default()
intents.message_content = True

class ECPayBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.ecpay_handler = None
        
    async def setup_hook(self):
        """Bot啟動時的設定"""
        # 使用runtime_config初始化ECPay處理器
        self.ecpay_handler = ECPayHandler()
        self.ecpay_handler.config = runtime_config.get('ECPAY_CONFIG', {})
        
        # 載入指令模塊
        from commands.payment_commands import setup
        await setup(self, self.ecpay_handler, runtime_config)
        
        await self.tree.sync()
        logger.info("Slash commands已同步")

    async def on_ready(self):
        """Bot準備就緒時觸發"""
        logger.info(f'{self.user} 已登入並準備就緒!')
        logger.info(f'Bot ID: {self.user.id}')
        
        # 設定Bot狀態
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"ECPay超商繳費服務 v{BOT_VERSION}"
            )
        )

bot = ECPayBot()

@bot.event
async def on_command_error(ctx, error):
    """錯誤處理"""
    logger.error(f"指令錯誤: {error}")

def main():
    """主函數"""
    global runtime_config
    
    # 載入基本配置
    from config import (
        DISCORD_BOT_TOKEN, ALLOWED_ROLE_IDS, ECPAY_CONFIG, 
        USE_TEST_ENVIRONMENT, USE_WEB_UI, WEB_UI_CONFIG, BOT_VERSION, BOT_OWNER_ID
    )
    runtime_config = {
        'DISCORD_BOT_TOKEN': DISCORD_BOT_TOKEN,
        'ALLOWED_ROLE_IDS': ALLOWED_ROLE_IDS,
        'ECPAY_CONFIG': ECPAY_CONFIG,
        'USE_TEST_ENVIRONMENT': USE_TEST_ENVIRONMENT,
        'BOT_OWNER_ID': BOT_OWNER_ID
    }
    
    print(f"🤖 ECPay Discord Bot v{BOT_VERSION}")
    print("=" * 50)
    print(f"📊 日誌等級: {LOG_CONFIG['level']}")
    print(f"📝 終端日誌: {'開啟' if LOG_CONFIG['show_console'] else '關閉'}")
    print(f"🔧 後端日誌: {'開啟' if LOG_CONFIG['show_backend'] else '關閉'}")
    print(f"📁 日誌檔案: {LOG_CONFIG['file']}")
    
    # 檢查配置模式
    if USE_WEB_UI:
        print("🖥️ 啟動WebUI配置模式...")
        print(f"📍 請開啟瀏覽器訪問: http://{WEB_UI_CONFIG['host']}:{WEB_UI_CONFIG['port']}")
        
        app = create_web_ui()
        
        # 在背景執行WebUI
        def run_web_ui():
            app.run(
                host=WEB_UI_CONFIG['host'],
                port=WEB_UI_CONFIG['port'],
                debug=WEB_UI_CONFIG['debug'],
                use_reloader=False
            )
        
        web_thread = threading.Thread(target=run_web_ui, daemon=True)
        web_thread.start()
        
        # 等待配置完成
        print("⏳ 等待WebUI配置完成...")
        while True:
            is_valid, message = check_config_validity()
            if is_valid:
                print("✅ 配置完成，啟動Bot...")
                break
            asyncio.sleep(2)
    
    else:
        # 終端配置模式
        is_valid, message = check_config_validity()
        if not is_valid:
            terminal_config()
    
    # 啟動Bot
    try:
        logger.info("正在啟動Discord Bot...")
        bot.run(runtime_config['DISCORD_BOT_TOKEN'])
    except Exception as e:
        logger.error(f"Bot啟動失敗: {e}")
        print(f"❌ 錯誤: {e}")
        print("請檢查您的Discord Bot Token是否正確")

if __name__ == "__main__":
    main() 