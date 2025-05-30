import discord
from discord.ext import commands
import tempfile
import os
import uuid
import logging
import psutil
import platform
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def check_permissions(interaction: discord.Interaction, allowed_roles) -> bool:
    """檢查使用者是否有權限使用指令"""
    if not interaction.user.roles:
        return False
    
    user_role_ids = [role.id for role in interaction.user.roles]
    return any(role_id in allowed_roles for role_id in user_role_ids)

def check_owner_permissions(interaction: discord.Interaction, owner_id) -> bool:
    """檢查使用者是否為bot擁有者"""
    return interaction.user.id == owner_id

def format_bytes(bytes_value):
    """格式化位元組為可讀格式"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def get_uptime():
    """取得系統運行時間"""
    boot_time = psutil.boot_time()
    uptime_seconds = datetime.now().timestamp() - boot_time
    uptime = timedelta(seconds=uptime_seconds)
    
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    return f"{days}天 {hours}小時 {minutes}分鐘"

class PaymentCommands(commands.Cog):
    def __init__(self, bot, ecpay_handler, runtime_config):
        self.bot = bot
        self.ecpay_handler = ecpay_handler
        self.runtime_config = runtime_config

    @discord.app_commands.command(name="help", description="顯示所有可用指令的說明")
    async def help_command(self, interaction: discord.Interaction):
        """顯示幫助指令"""
        from config import BOT_VERSION
        
        embed = discord.Embed(
            title="🤖 ECPay Discord Bot 指令說明",
            description=f"**版本:** {BOT_VERSION}\n以下是所有可用的指令：",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        # 一般指令
        embed.add_field(
            name="💳 繳費相關指令",
            value="`/建立繳費單` - 建立ECPay超商繳費單\n`/查詢付款狀態` - 查詢付款狀態\n`/繳費說明` - 顯示繳費功能說明",
            inline=False
        )
        
        # 資訊指令
        embed.add_field(
            name="ℹ️ 資訊指令",
            value="`/help` - 顯示此說明\n`/機器人資訊` - 查看機器人詳細資訊",
            inline=False
        )
        
        # 管理指令（僅擁有者可見）
        if check_owner_permissions(interaction, self.runtime_config.get('BOT_OWNER_ID', 0)):
            embed.add_field(
                name="🔧 管理指令（僅擁有者）",
                value="`/系統狀況` - 查看伺服器系統狀況",
                inline=False
            )
        
        embed.add_field(
            name="🏪 支援超商",
            value="• 🏪 全通用（所有超商）\n• 🏪 7-ELEVEN (ibon機台)\n• 🏪 全家便利商店\n• 🏪 萊爾富\n• 🏪 OK便利商店",
            inline=False
        )
        
        embed.add_field(
            name="💰 付款限制",
            value="• 最低金額: NT$ 1\n• 最高金額: NT$ 20,000\n• 繳費期限: 7天",
            inline=False
        )
        
        embed.add_field(
            name="📱 超商選擇功能",
            value="• 可指定特定超商繳費\n• 不同超商有專屬繳費代碼\n• 提供詳細操作指南\n• 支援全通用模式",
            inline=False
        )
        
        embed.set_footer(text=f"ECPay Discord Bot v{BOT_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @discord.app_commands.command(name="機器人資訊", description="查看機器人詳細資訊")
    async def bot_info(self, interaction: discord.Interaction):
        """顯示機器人資訊"""
        from config import BOT_VERSION, USE_TEST_ENVIRONMENT
        
        # 計算機器人運行時間
        if hasattr(self.bot, 'start_time'):
            uptime = datetime.now() - self.bot.start_time
            uptime_str = f"{uptime.days}天 {uptime.seconds//3600}小時 {(uptime.seconds//60)%60}分鐘"
        else:
            uptime_str = "未知"
        
        embed = discord.Embed(
            title="🤖 機器人資訊",
            description="ECPay Discord Bot 詳細資訊",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        # 基本資訊
        embed.add_field(
            name="📋 基本資訊",
            value=f"**名稱:** {self.bot.user.name}\n**ID:** {self.bot.user.id}\n**版本:** {BOT_VERSION}\n**運行時間:** {uptime_str}",
            inline=False
        )
        
        # 伺服器統計
        guild_count = len(self.bot.guilds)
        user_count = sum(guild.member_count for guild in self.bot.guilds)
        
        embed.add_field(
            name="📊 統計資訊",
            value=f"**伺服器數量:** {guild_count}\n**用戶數量:** {user_count:,}\n**延遲:** {round(self.bot.latency * 1000)}ms",
            inline=False
        )
        
        # 系統資訊
        embed.add_field(
            name="💻 系統資訊",
            value=f"**Python版本:** {platform.python_version()}\n**Discord.py版本:** {discord.__version__}\n**作業系統:** {platform.system()} {platform.release()}",
            inline=False
        )
        
        # ECPay設定
        embed.add_field(
            name="💳 ECPay設定",
            value=f"**環境:** {'測試環境' if USE_TEST_ENVIRONMENT else '正式環境'}\n**商店代號:** {self.runtime_config.get('ECPAY_CONFIG', {}).get('MerchantID', 'N/A')}\n**繳費期限:** {self.runtime_config.get('ECPAY_CONFIG', {}).get('ExpireDate', 7)}天",
            inline=False
        )
        
        # 功能狀態
        embed.add_field(
            name="🔧 功能狀態",
            value="✅ ECPay整合\n✅ 超商選擇\n✅ 權限控制\n✅ 日誌系統\n✅ WebUI配置",
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text=f"查詢者: {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @discord.app_commands.command(name="系統狀況", description="查看伺服器系統狀況（僅擁有者）")
    async def system_status(self, interaction: discord.Interaction):
        """查看系統狀況（僅擁有者可用）"""
        # 檢查擁有者權限
        owner_id = self.runtime_config.get('BOT_OWNER_ID', 0)
        if not check_owner_permissions(interaction, owner_id):
            await interaction.response.send_message("❌ 此指令僅限機器人擁有者使用！", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=False)
        
        try:
            # 取得系統資訊
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 取得網路資訊
            net_io = psutil.net_io_counters()
            
            # 取得程序資訊
            process = psutil.Process()
            process_memory = process.memory_info()
            
            embed = discord.Embed(
                title="🖥️ 系統狀況監控",
                description="伺服器即時系統狀況",
                color=0xff6600,
                timestamp=datetime.now()
            )
            
            # CPU資訊
            cpu_emoji = "🟢" if cpu_percent < 50 else "🟡" if cpu_percent < 80 else "🔴"
            embed.add_field(
                name=f"{cpu_emoji} CPU使用率",
                value=f"**使用率:** {cpu_percent}%\n**核心數:** {psutil.cpu_count()}\n**邏輯核心:** {psutil.cpu_count(logical=True)}",
                inline=True
            )
            
            # 記憶體資訊
            memory_percent = memory.percent
            memory_emoji = "🟢" if memory_percent < 50 else "🟡" if memory_percent < 80 else "🔴"
            embed.add_field(
                name=f"{memory_emoji} 記憶體使用",
                value=f"**使用率:** {memory_percent}%\n**已使用:** {format_bytes(memory.used)}\n**總容量:** {format_bytes(memory.total)}",
                inline=True
            )
            
            # 磁碟資訊
            disk_percent = disk.percent
            disk_emoji = "🟢" if disk_percent < 50 else "🟡" if disk_percent < 80 else "🔴"
            embed.add_field(
                name=f"{disk_emoji} 磁碟使用",
                value=f"**使用率:** {disk_percent}%\n**已使用:** {format_bytes(disk.used)}\n**總容量:** {format_bytes(disk.total)}",
                inline=True
            )
            
            # 系統資訊
            embed.add_field(
                name="💻 系統資訊",
                value=f"**作業系統:** {platform.system()} {platform.release()}\n**架構:** {platform.machine()}\n**運行時間:** {get_uptime()}",
                inline=True
            )
            
            # 網路資訊
            embed.add_field(
                name="🌐 網路統計",
                value=f"**發送:** {format_bytes(net_io.bytes_sent)}\n**接收:** {format_bytes(net_io.bytes_recv)}\n**封包發送:** {net_io.packets_sent:,}",
                inline=True
            )
            
            # Bot程序資訊
            embed.add_field(
                name="🤖 Bot程序",
                value=f"**記憶體使用:** {format_bytes(process_memory.rss)}\n**虛擬記憶體:** {format_bytes(process_memory.vms)}\n**CPU使用率:** {process.cpu_percent()}%",
                inline=True
            )
            
            # 溫度資訊（如果可用）
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    temp_info = []
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current:
                                temp_emoji = "🟢" if entry.current < 60 else "🟡" if entry.current < 80 else "🔴"
                                temp_info.append(f"{temp_emoji} {entry.label or name}: {entry.current}°C")
                    
                    if temp_info:
                        embed.add_field(
                            name="🌡️ 溫度監控",
                            value="\n".join(temp_info[:3]),  # 最多顯示3個溫度
                            inline=False
                        )
            except:
                pass  # 溫度資訊不可用時忽略
            
            # 系統負載（Linux/Unix）
            try:
                load_avg = os.getloadavg()
                embed.add_field(
                    name="⚖️ 系統負載",
                    value=f"**1分鐘:** {load_avg[0]:.2f}\n**5分鐘:** {load_avg[1]:.2f}\n**15分鐘:** {load_avg[2]:.2f}",
                    inline=True
                )
            except:
                pass  # Windows系統沒有loadavg
            
            embed.set_footer(text=f"查詢者: {interaction.user.display_name} | 更新時間")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"取得系統狀況時發生錯誤: {e}")
            await interaction.followup.send("❌ 取得系統狀況時發生錯誤！")

    @discord.app_commands.command(name="建立繳費單", description="建立ECPay超商繳費單")
    @discord.app_commands.describe(
        金額="繳費金額（1-20000元）",
        說明="交易說明",
        商品名稱="商品名稱",
        超商選擇="選擇指定超商或全通用"
    )
    @discord.app_commands.choices(超商選擇=[
        discord.app_commands.Choice(name="🏪 全通用（所有超商）", value="ALL"),
        discord.app_commands.Choice(name="🏪 7-ELEVEN（ibon機台）", value="SEVEN"),
        discord.app_commands.Choice(name="🏪 全家便利商店", value="FAMILY"),
        discord.app_commands.Choice(name="🏪 萊爾富", value="HILIFE"),
        discord.app_commands.Choice(name="🏪 OK便利商店", value="OK")
    ])
    async def create_payment(
        self,
        interaction: discord.Interaction,
        金額: int,
        說明: str,
        超商選擇: discord.app_commands.Choice[str],
        商品名稱: str = "商品"
    ):
        """建立付款單指令"""
        # 檢查權限
        allowed_roles = self.runtime_config.get('ALLOWED_ROLE_IDS', [])
        if not check_permissions(interaction, allowed_roles):
            await interaction.response.send_message("❌ 您沒有權限使用此指令！", ephemeral=True)
            return
        
        # 檢查金額
        if 金額 <= 0:
            await interaction.response.send_message("❌ 金額必須大於0！", ephemeral=True)
            return
        
        if 金額 > 20000:
            await interaction.response.send_message("❌ 超商繳費金額不能超過20,000元！", ephemeral=True)
            return
        
        try:
            await interaction.response.defer(ephemeral=False)  # 改為公開可見
            
            # 產生唯一交易編號
            trade_no = f"DC{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8]}"
            
            # 建立付款表單
            form_html, params, order_info = self.ecpay_handler.generate_payment_url(
                trade_no=trade_no,
                total_amount=金額,
                trade_desc=說明,
                item_name=商品名稱,
                store_type=超商選擇.value
            )
            
            # 格式化付款資訊
            payment_info = self.ecpay_handler.format_payment_info(order_info)
            
            # 根據超商選擇設定顏色和標題
            store_info = self.get_store_info(超商選擇.value)
            
            # 建立詳細的嵌入訊息
            embed = discord.Embed(
                title=f"💳 ECPay超商繳費單 - {store_info['name']}",
                description=store_info['description'],
                color=store_info['color'],
                timestamp=datetime.now()
            )
            
            # 根據超商類型顯示相應的繳費代碼
            if 超商選擇.value == "ALL":
                # 全通用 - 顯示所有代碼
                embed.add_field(
                    name="🏪 ibon機台繳費代碼（7-ELEVEN）",
                    value=f"```{payment_info['ibon_code']}```",
                    inline=False
                )
                embed.add_field(
                    name="🔢 其他超商繳費代碼",
                    value=f"```{payment_info['payment_code']}```",
                    inline=False
                )
            elif 超商選擇.value == "SEVEN":
                # 7-ELEVEN專用
                embed.add_field(
                    name="🏪 ibon機台繳費代碼",
                    value=f"```{payment_info['ibon_code']}```",
                    inline=False
                )
            else:
                # 其他超商
                embed.add_field(
                    name="🔢 超商繳費代碼",
                    value=f"```{payment_info['payment_code']}```",
                    inline=False
                )
            
            # 訂單基本資訊
            embed.add_field(
                name="📋 訂單資訊",
                value=f"**🆔 訂單編號:** `{payment_info['trade_no']}`\n**🛍️ 商品名稱:** {payment_info['item_name']}\n**💰 交易金額:** NT$ {payment_info['total_amount']:,}\n**🏪 指定超商:** {store_info['name']}",
                inline=False
            )
            
            # 時間資訊
            embed.add_field(
                name="⏰ 時間資訊",
                value=f"**📅 訂單產生時間:** {payment_info['create_time']}\n**⏳ 訂單有效期限:** {payment_info['expire_date']}\n**❌ 訂單失效時間:** {payment_info['expire_time']}",
                inline=False
            )
            
            # 根據超商類型顯示相應的使用說明
            if 超商選擇.value == "ALL":
                # 全通用說明
                embed.add_field(
                    name="🏪 繳費步驟",
                    value="**ibon機台（7-ELEVEN）:**\n使用14位數ibon代碼\n\n**其他超商（全家/萊爾富/OK）:**\n使用一般繳費代碼，告知店員「代碼繳費」",
                    inline=False
                )
            elif 超商選擇.value == "SEVEN":
                # 7-ELEVEN專用說明
                embed.add_field(
                    name="📱 ibon機台繳費步驟",
                    value="1️⃣ 前往7-ELEVEN找到ibon機台\n2️⃣ 點選「儲值/繳費」\n3️⃣ 選擇「繳費」\n4️⃣ 選擇「輸入代碼」\n5️⃣ 輸入上方14位數繳費代碼\n6️⃣ 確認金額後列印繳費單\n7️⃣ 持繳費單至櫃台付款",
                    inline=False
                )
            else:
                # 其他超商專用說明
                store_steps = self.get_store_steps(超商選擇.value)
                embed.add_field(
                    name=f"🏪 {store_info['name']}繳費步驟",
                    value=store_steps,
                    inline=False
                )
            
            embed.set_footer(text=f"建立者: {interaction.user.display_name}")
            
            # 建立臨時HTML檔案（備用）
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(form_html)
                temp_file_path = f.name
            
            # 發送嵌入訊息和檔案
            with open(temp_file_path, 'rb') as f:
                file = discord.File(f, filename=f"ecpay_payment_{trade_no}.html")
                await interaction.followup.send(
                    content=f"✅ **繳費單已建立完成！** <@{interaction.user.id}>\n\n⚠️ **重要提醒：**\n• 請在期限內完成繳費\n• 繳費代碼僅能使用一次\n• 如有問題請聯繫客服",
                    embed=embed, 
                    file=file
                )
            
            # 清理臨時檔案
            os.unlink(temp_file_path)
            
            logger.info(f"使用者 {interaction.user} 建立了付款單: {trade_no}, 金額: {金額}, 超商: {超商選擇.name}")
            
        except Exception as e:
            logger.error(f"建立付款單時發生錯誤: {e}")
            await interaction.followup.send("❌ 建立付款單時發生錯誤，請稍後再試！")

    def get_store_info(self, store_type):
        """取得超商資訊"""
        store_map = {
            "ALL": {
                "name": "全通用",
                "description": "可在所有支援的超商繳費",
                "color": 0x00ff00
            },
            "SEVEN": {
                "name": "7-ELEVEN",
                "description": "專用於7-ELEVEN ibon機台繳費",
                "color": 0xff6600
            },
            "FAMILY": {
                "name": "全家便利商店",
                "description": "專用於全家便利商店繳費",
                "color": 0x0066ff
            },
            "HILIFE": {
                "name": "萊爾富",
                "description": "專用於萊爾富便利商店繳費",
                "color": 0xff0066
            },
            "OK": {
                "name": "OK便利商店",
                "description": "專用於OK便利商店繳費",
                "color": 0x66ff00
            }
        }
        return store_map.get(store_type, store_map["ALL"])

    def get_store_steps(self, store_type):
        """取得超商繳費步驟"""
        steps_map = {
            "FAMILY": "1️⃣ 前往全家便利商店\n2️⃣ 告知店員「代碼繳費」\n3️⃣ 提供繳費代碼給店員\n4️⃣ 確認金額後完成繳費\n5️⃣ 保留收據作為憑證",
            "HILIFE": "1️⃣ 前往萊爾富便利商店\n2️⃣ 告知店員「代碼繳費」\n3️⃣ 提供繳費代碼給店員\n4️⃣ 確認金額後完成繳費\n5️⃣ 保留收據作為憑證",
            "OK": "1️⃣ 前往OK便利商店\n2️⃣ 告知店員「代碼繳費」\n3️⃣ 提供繳費代碼給店員\n4️⃣ 確認金額後完成繳費\n5️⃣ 保留收據作為憑證"
        }
        return steps_map.get(store_type, "1️⃣ 前往指定超商\n2️⃣ 告知店員「代碼繳費」\n3️⃣ 提供繳費代碼\n4️⃣ 完成繳費")

    @discord.app_commands.command(name="查詢付款狀態", description="查詢付款狀態")
    async def payment_status(self, interaction: discord.Interaction, 交易編號: str):
        """查詢付款狀態指令"""
        # 檢查權限
        allowed_roles = self.runtime_config.get('ALLOWED_ROLE_IDS', [])
        if not check_permissions(interaction, allowed_roles):
            await interaction.response.send_message("❌ 您沒有權限使用此指令！", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=False)  # 改為公開可見
        
        embed = discord.Embed(
            title="🔍 付款狀態查詢",
            description=f"**交易編號:** `{交易編號}`",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📊 狀態",
            value="請至ECPay後台查詢詳細付款狀態\n或聯繫客服確認繳費情況",
            inline=False
        )
        
        embed.set_footer(text=f"查詢者: {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="繳費說明", description="顯示ECPay指令說明")
    async def help_ecpay(self, interaction: discord.Interaction):
        """說明指令"""
        from config import BOT_VERSION
        
        embed = discord.Embed(
            title="📚 ECPay Discord Bot 使用說明",
            description=f"這個Bot可以幫助您建立ECPay超商繳費單\n**版本:** {BOT_VERSION}",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🔧 可用指令",
            value="`/建立繳費單` - 建立付款單\n`/查詢付款狀態` - 查詢付款狀態\n`/繳費說明` - 顯示此說明",
            inline=False
        )
        
        embed.add_field(
            name="💰 付款限制",
            value="• 最低金額: NT$ 1\n• 最高金額: NT$ 20,000\n• 繳費期限: 7天",
            inline=False
        )
        
        embed.add_field(
            name="🏪 支援超商",
            value="• 🏪 全通用（所有超商）\n• 🏪 7-ELEVEN (ibon機台)\n• 🏪 全家便利商店\n• 🏪 萊爾富\n• 🏪 OK便利商店",
            inline=False
        )
        
        embed.add_field(
            name="📱 超商選擇功能",
            value="• 可指定特定超商繳費\n• 不同超商有專屬繳費代碼\n• 提供詳細操作指南\n• 支援全通用模式",
            inline=False
        )
        
        embed.set_footer(text=f"ECPay Discord Bot v{BOT_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=False)  # 改為公開可見

async def setup(bot, ecpay_handler, runtime_config):
    """設定指令模塊"""
    await bot.add_cog(PaymentCommands(bot, ecpay_handler, runtime_config)) 