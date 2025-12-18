# MENU CRACK INTERAKTIF
# Menampilkan menu submenu setelah kategori dipilih

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import aiohttp
import redis.asyncio as redis
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils import executor
import sys

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Configuration
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8548539065:AAHLcyMQKHimwo1cLTuUKZl8OR1xngL_GeI")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:5000")

# Initialize bot
bot = Bot(token=API_TOKEN)
storage = RedisStorage2(REDIS_URL)
dp = Dispatcher(bot, storage=storage)

# Enums for categories
class CrackCategory:
    LOGIN_BYPASS = "🔓 LOGIN BYPASS"
    IAP_CRACK = "💰 IN-APP PURCHASE CRACK"
    GAME_MODS = "🎮 GAME MODS"
    PREMIUM_UNLOCK = "📺 PREMIUM FEATURE UNLOCK"
    ROOT_BYPASS = "🛡️ ROOT/JAILBREAK BYPASS"
    LICENSE_CRACK = "🔐 LICENSE CRACK"
    SYSTEM_MODS = "📱 SYSTEM MODIFICATIONS"
    MEDIA_CRACK = "🎵 MEDIA CRACK"
    DATA_EXTRACTION = "💾 DATA EXTRACTION"
    NETWORK_BYPASS = "🌐 NETWORK BYPASS"
    PERFORMANCE_BOOST = "⚡ PERFORMANCE BOOST"
    AI_ENHANCED = "🧠 AI-ENHANCED CRACK"
    ADS_REMOVAL = "🚫 ADS/TRACKING REMOVAL"
    CUSTOM_CRACK = "🔧 CUSTOM CRACK"
    AUTO_DETECT = "🔄 AUTO-DETECT MODE"

# Subcategory patterns for each main category
SUBCATEGORY_PATTERNS = {
    CrackCategory.LOGIN_BYPASS: [
        ("🔐 Auto-Login Bypass", "auto_login_bypass"),
        ("🔑 Password Cracker", "password_crack"),
        ("📱 Biometric Bypass", "biometric_bypass"),
        ("🔒 2FA/OTP Bypass", "otp_bypass"),
        ("👤 Session Hijacking", "session_hijack"),
        ("🎭 Credential Generator", "cred_generator"),
        ("🤖 Social Login Crack", "social_login_crack"),
        ("🎟️ JWT Token Manipulation", "jwt_manipulation")
    ],
    
    CrackCategory.IAP_CRACK: [
        ("🛒 Google Play Billing Bypass", "google_billing_bypass"),
        ("🍎 App Store Receipt Bypass", "appstore_receipt_bypass"),
        ("📱 Local Validation Crack", "local_validation_crack"),
        ("🌐 Server-Side Bypass", "server_side_bypass"),
        ("💰 Subscription Free", "subscription_free"),
        ("🎁 Consumable Items Unlimited", "unlimited_items"),
        ("🧾 Receipt Generator", "receipt_generator"),
        ("⏰ Trial Period Remove", "trial_period_remove")
    ],
    
    CrackCategory.GAME_MODS: [
        ("💰 Unlimited Coins/Gems", "unlimited_coins"),
        ("💎 All Items Unlocked", "all_items_unlocked"),
        ("👑 Premium Features Unlock", "game_premium_unlock"),
        ("⚡ God Mode/No Damage", "god_mode"),
        ("🚀 Speed Hack", "speed_hack"),
        ("🎯 Auto-Aim/Auto-Play", "auto_aim"),
        ("🛡️ Anti-Ban Protection", "anti_ban"),
        ("📊 Stats Editor", "stats_editor")
    ],
    
    CrackCategory.PREMIUM_UNLOCK: [
        ("🎵 Spotify/Apple Music Premium", "music_premium"),
        ("📺 Netflix/Disney+ Premium", "video_premium"),
        ("📱 YouTube Premium/Red", "youtube_premium"),
        ("💬 WhatsApp/Telegram Premium", "chat_premium"),
        ("📸 Instagram/TikTok Premium", "social_premium"),
        ("📧 Email Premium", "email_premium"),
        ("📁 Cloud Storage Premium", "cloud_premium"),
        ("🎨 Photo/Video Editor Premium", "editor_premium")
    ],
    
    CrackCategory.ROOT_BYPASS: [
        ("🛡️ Root Detection Bypass", "root_detection_bypass"),
        ("📱 Samsung KNOX Bypass", "knock_bypass"),
        ("🤖 SuperSU Detection Bypass", "supersu_bypass"),
        ("🔍 RootBeer Bypass", "rootbeer_bypass"),
        ("📱 Magisk Hide", "magisk_hide"),
        ("🛡️ SafetyNet Bypass", "safetynet_bypass"),
        ("🔍 Xposed Detection Bypass", "xposed_bypass"),
        ("📱 Device Owner Bypass", "device_owner_bypass")
    ],
    
    CrackCategory.LICENSE_CRACK: [
        ("🔐 License Checker Bypass", "license_bypass"),
        ("📱 Play Store License Bypass", "play_license_bypass"),
        ("🤖 Custom License System Crack", "custom_license_crack"),
        ("🔑 API Key Generation", "api_key_gen"),
        ("🔐 Offline License Activation", "offline_activation"),
        ("📱 Fake License Response", "fake_license"),
        ("🔒 Signature Verification Bypass", "sig_bypass"),
        ("🔐 Trial Reset", "trial_reset")
    ],
    
    CrackCategory.SYSTEM_MODS: [
        ("📱 Permissions Manager", "perm_manager"),
        ("🔔 Notification Control", "notification_control"),
        ("🔋 Battery Optimization Bypass", "battery_opt_bypass"),
        ("📊 Data Usage Modification", "data_usage_mod"),
        ("💾 Storage Permission Bypass", "storage_perm_bypass"),
        ("📷 Camera/Mic Access", "camera_mic_access"),
        ("📍 Location Spoofing", "location_spoof"),
        ("📱 Device Info Modification", "device_info_mod")
    ],
    
    CrackCategory.MEDIA_CRACK: [
        ("🎬 DRM Removal", "drm_removal"),
        ("📥 Download Unlocked", "download_unlocked"),
        ("📺 Quality Unlock (4K/HD)", "quality_unlock"),
        ("🚫 Ads Removal", "ads_removal"),
        ("📱 Offline Playback", "offline_playback"),
        ("🌍 Region Restriction Bypass", "region_bypass"),
        ("💧 Watermark Removal", "watermark_removal"),
        ("🔄 Format Conversion", "format_conversion")
    ],
    
    CrackCategory.DATA_EXTRACTION: [
        ("🗄️ Database Extraction", "db_extraction"),
        ("📋 Shared Preferences", "shared_pref_extraction"),
        ("💾 Internal Storage Access", "internal_storage"),
        ("📤 External Storage Access", "external_storage"),
        ("📦 Cache Files Extraction", "cache_extraction"),
        ("📝 Log Files Extraction", "log_extraction"),
        ("⚙️ Config Files Access", "config_access"),
        ("🖼️ Assets Extraction", "asset_extraction")
    ],
    
    CrackCategory.NETWORK_BYPASS: [
        ("_tls Certificate Pinning Bypass", "ssl_pinning_bypass"),
        ("🌐 Proxy Detection Bypass", "proxy_bypass"),
        ("🔒 VPN Detection Bypass", "vpn_bypass"),
        ("🔥 Firewall Bypass", "firewall_bypass"),
        ("⚡ Rate Limiting Bypass", "rate_limit_bypass"),
        ("🔐 API Key Extraction", "api_key_extraction"),
        ("📡 Network Traffic Intercept", "traffic_intercept"),
        ("🔒 Security Header Bypass", "header_bypass")
    ],
    
    CrackCategory.PERFORMANCE_BOOST: [
        ("⚡ Speed Optimization", "speed_opt"),
        ("🧠 Memory Management", "memory_mgmt"),
        ("🔥 GPU Acceleration", "gpu_accel"),
        ("🔄 Multi-Threading", "multithreading"),
        ("⚡ CPU Frequency Boost", "cpu_boost"),
        ("🔋 Battery Life Improvement", "battery_improve"),
        ("📊 Resource Optimization", "resource_opt"),
        ("🚀 Loading Speed Boost", "load_boost")
    ],
    
    CrackCategory.AI_ENHANCED: [
        ("🧠 DeepSeek AI Analysis", "deepseek_analysis"),
        ("👾 WormGPT Crack Pattern", "wormgpt_pattern"),
        ("🤖 Dual AI Coordination", "dual_ai_coord"),
        ("🎯 AI-Powered Automation", "ai_automation"),
        ("🧠 Neural Pattern Recognition", "neural_pattern"),
        ("🤖 Predictive Cracking", "predictive_crack"),
        ("🧠 AI Decision Making", "ai_decision"),
        ("🤖 Machine Learning Bypass", "ml_bypass")
    ],
    
    CrackCategory.ADS_REMOVAL: [
        ("🚫 AdMob Banner Removal", "admob_banner"),
        ("🚫 Interstitial Removal", "interstitial_remove"),
        ("🚫 Reward Ad Removal", "reward_ad_remove"),
        ("🚫 Native Ad Removal", "native_ad_remove"),
        ("🚫 Tracking Removal", "tracking_remove"),
        ("🚫 Analytics Removal", "analytics_remove"),
        ("🚫 Push Notification Ads", "push_ads_remove"),
        ("🚫 In-App Banner Removal", "inapp_banner_remove")
    ]
}

# State management
class CrackStates(StatesGroup):
    SELECTING_CATEGORY = State()
    SELECTING_SUBCATEGORY = State()  
    UPLOADING_APK = State()
    ANALYZING = State()
    CUSTOMIZING_FIXES = State()
    PROCESSING = State()
    DOWNLOADING = State()

# Main bot class
class CyberCrackBot:
    def __init__(self):
        self.http_session = None
        self.redis_client = None
    
    async def initialize(self):
        self.http_session = aiohttp.ClientSession()
        self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    
    async def close(self):
        if self.http_session:
            await self.http_session.close()
        if self.redis_client:
            await self.redis_client.close()

    async def create_main_menu(self) -> ReplyKeyboardMarkup:
        """Create main category menu"""
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        categories = [
            CrackCategory.LOGIN_BYPASS,
            CrackCategory.IAP_CRACK,
            CrackCategory.GAME_MODS,
            CrackCategory.PREMIUM_UNLOCK,
            CrackCategory.ROOT_BYPASS,
            CrackCategory.LICENSE_CRACK,
            CrackCategory.SYSTEM_MODS,
            CrackCategory.MEDIA_CRACK,
            CrackCategory.DATA_EXTRACTION,
            CrackCategory.NETWORK_BYPASS,
            CrackCategory.PERFORMANCE_BOOST,
            CrackCategory.AI_ENHANCED,
            CrackCategory.ADS_REMOVAL,
            CrackCategory.CUSTOM_CRACK,
            CrackCategory.AUTO_DETECT
        ]
        
        for category in categories:
            keyboard.add(KeyboardButton(category))
        
        keyboard.add(
            KeyboardButton("📊 My Jobs"),
            KeyboardButton("⚙️ Settings"),
            KeyboardButton("❓ Help"),
            KeyboardButton("📖 About")
        )
        
        return keyboard

    async def create_subcategory_menu(self, category: str) -> InlineKeyboardMarkup:
        """Create inline keyboard for subcategories"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        # Find category in our enum
        selected_cat = None
        for cat_attr in dir(CrackCategory):
            cat_value = getattr(CrackCategory, cat_attr)
            if cat_value == category:
                selected_cat = cat_value
                break
        
        if selected_cat and selected_cat in SUBCATEGORY_PATTERNS:
            subcategories = SUBCATEGORY_PATTERNS[selected_cat]
            for text, callback in subcategories:
                keyboard.add(InlineKeyboardButton(text, callback_data=f"subcat_{callback}"))
        
        # Add navigation buttons
        keyboard.row(
            InlineKeyboardButton("⬅️ Back to Categories", callback_data="back_to_categories"),
            InlineKeyboardButton("🤖 AI Auto-Detect", callback_data="ai_auto_detect")
        )
        
        return keyboard

bot_manager = CyberCrackBot()

# HANDLERS

 @dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: types.Message):
    """Start command handler - show welcome and category menu"""
    welcome_text = """
🚀 **CYBER CRACK PRO v3.0** 🚀

⚡ **Ultra-Fast APK Cracking System**
✅ 100+ Cracking Features
🤖 **AI-Powered Analysis (Dual AI)**
🔒 Auto-Stability Protection
⚡ Multi-Language Processing (Go, Rust, C++, Java)

📋 **Available Categories:**
• 🔓 Login/Authentication Bypass
• 💰 In-App Purchase Cracking  
• 🎮 Game Modifications
• 📺 Premium Feature Unlock
• 🛡️ Root/Jailbreak Bypass
• 🔐 License Cracking
• 📱 System Modifications
• 🎵 Media Cracking
• 💾 Data Extraction
• 🌐 Network Security Bypass
• ⚡ Performance Boosting
• 🧠 AI-Enhanced Cracking
• 🚫 Ads/Tracking Removal

🎯 **How to Use:**
1. Select category from menu below
2. Choose specific subcategory
3. Upload your APK file
4. Get AI-powered modifications
5. Download cracked APK

⚠️ **For educational purposes only**
"""
    
    # Send welcome message
    await message.answer(welcome_text, parse_mode='Markdown')
    
    # Send category menu
    category_menu = await bot_manager.create_main_menu()
    await message.answer("🎯 **SELECT CRACK CATEGORY:**", reply_markup=category_menu)
    
    await CrackStates.SELECTING_CATEGORY.set()

 @dp.message_handler(state=CrackStates.SELECTING_CATEGORY)
async def handle_category_selection(message: types.Message, state: FSMContext):
    """Handle category selection from main menu"""
    selected_category = message.text
    
    # Validate if it's a valid category
    valid_categories = [getattr(CrackCategory, attr) for attr in dir(CrackCategory) 
                       if not attr.startswith('_')]
    
    if selected_category not in valid_categories:
        if selected_category in ["📊 My Jobs", "⚙️ Settings", "❓ Help", "📖 About"]:
            # Handle utility commands
            await handle_utility_command(message, state, selected_category)
            return
        
        await message.answer("❌ Invalid category. Please select from the menu.")
        return
    
    # Store category in state
    await state.update_data(selected_category=selected_category)
    
    # Show subcategory menu
    subcategory_menu = await bot_manager.create_subcategory_menu(selected_category)
    
    category_name = selected_category.replace(" ", "_").upper()
    
    subcat_text = f"""
🎯 **{selected_category} SELECTED**

**Available Subcategories:**
"""
    
    # Show subcategory details
    selected_cat_key = None
    for cat_attr in dir(CrackCategory):
        cat_value = getattr(CrackCategory, cat_attr)
        if cat_value == selected_category:
            selected_cat_key = cat_value
            break
    
    if selected_cat_key and selected_cat_key in SUBCATEGORY_PATTERNS:
        for i, (text, _) in enumerate(SUBCATEGORY_PATTERNS[selected_cat_key][:4], 1):
            subcat_text += f"{i}. {text}\n"
        
        if len(SUBCATEGORY_PATTERNS[selected_cat_key]) > 4:
            subcat_text += f"... and {len(SUBCATEGORY_PATTERNS[selected_cat_key]) - 4} more\n"
    
    subcat_text += "\n👆 Select specific feature from inline menu below:"
    
    await message.answer(subcat_text, reply_markup=subcategory_menu, parse_mode='Markdown')
    await CrackStates.SELECTING_SUBCATEGORY.set()

async def handle_utility_command(message: types.Message, state: FSMContext, command: str):
    """Handle utility commands like My Jobs, Settings, etc."""
    if command == "📊 My Jobs":
        await message.answer("📋 Your recent jobs will be displayed here\n(Coming soon in full implementation)")
    elif command == "⚙️ Settings":
        await message.answer("🔧 Settings menu coming soon\nUse /settings command")
    elif command == "❓ Help":
        await message.answer("ℹ️ Help information:\n- Use menu buttons to select category\n- Upload .apk files for cracking\n- Get AI-powered results")
    elif command == "📖 About":
        await message.answer("ℹ️ Cyber Crack Pro v3.0\nMulti-engine AI-powered APK cracker")

 @dp.callback_query_handler(lambda c: c.data.startswith('subcat_'), state=CrackStates.SELECTING_SUBCATEGORY)
async def handle_subcategory_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle subcategory selection"""
    
    subcategory = callback_query.data.replace('subcat_', '')
    await bot.answer_callback_query(callback_query.id, f"Selected: {subcategory}")
    
    # Store subcategory in state
    await state.update_data(selected_subcategory=subcategory)
    
    # Ask for APK upload
    upload_text = f"""
📤 **UPLOAD APK FOR {callback_query.data.replace('subcat_', '').upper().replace('_', ' ')}**

**Requirements:**
• File format: .apk only
• Size limit: 500MB max
• Target: Android app to crack
• Must be decompilable APK

**Processing:**
• AI analysis: 3-8 seconds
• Modification: 5-15 seconds
• Total time: 8-20 seconds
• Success rate: 95%+

⚠️ **Note**: Only upload apps you own or have permission to analyze
"""
    
    await callback_query.message.answer(upload_text, parse_mode='Markdown')
    
    # Switch to uploading state
    await CrackStates.UPLOADING_APK.set()

 @dp.callback_query_handler(lambda c: c.data == "back_to_categories", state='*')
async def back_to_categories(callback_query: types.CallbackQuery, state: FSMContext):
    """Return to category selection"""
    await bot.answer_callback_query(callback_query.id)
    
    category_menu = await bot_manager.create_main_menu()
    await callback_query.message.answer("🎯 **SELECT CRACK CATEGORY:**", reply_markup=category_menu)
    
    await CrackStates.SELECTING_CATEGORY.set()

 @dp.callback_query_handler(lambda c: c.data == "ai_auto_detect", state=CrackStates.SELECTING_SUBCATEGORY)
async def handle_ai_auto_detect(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle AI auto-detection"""
    await bot.answer_callback_query(callback_query.id, "🤖 AI Auto-detecting...")
    
    # Update state to auto-detect mode
    await state.update_data(selected_category="AUTO_DETECT", selected_subcategory="auto_ai")
    
    # Ask for APK upload
    await callback_query.message.answer("""
📤 **AUTO-DETECTION MODE ACTIVATED**

🤖 **AI will automatically detect:**
• App type and category
• Security measures present
• Optimal crack methods
• Recommended modifications

**Upload your APK to begin analysis:**
• File format: .apk only
• Size limit: 500MB max
• Processing time: 5-15 seconds
• AI confidence: 90%+
""")
    
    await CrackStates.UPLOADING_APK.set()

 @dp.message_handler(content_types=['document'], state=CrackStates.UPLOADING_APK)
async def handle_apk_upload(message: types.Message, state: FSMContext):
    """Handle APK file upload"""
    user_id = message.from_user.id
    file_name = message.document.file_name
    
    # Validate .apk file
    if not file_name.lower().endswith('.apk'):
        await message.answer("❌ Please upload a .apk file!")
        return
    
    # Create user upload directory
    user_dir = Path("uploads") / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = user_dir / f"{timestamp}_{file_name}"
    
    try:
        # Download file
        file_info = await bot.get_file(message.document.file_id)
        await bot.download_file(file_info.file_path, file_path)
        
        # Validate file size
        file_size = file_path.stat().st_size
        if file_size > 500 * 1024 * 1024:  # 500MB
            await message.answer("❌ File too large! Maximum 500MB.")
            file_path.unlink()  # Delete the file
            return
        
        # Store file info in state
        await state.update_data({
            'apk_path': str(file_path),
            'original_name': file_name,
            'file_size': file_size
        })
        
        # Start analysis
        await start_analysis_process(message, state)
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        await message.answer("❌ Error uploading file. Please try again.")

async def start_analysis_process(message: types.Message, state: FSMContext):
    """Start the analysis process with dual AI"""
    user_data = await state.get_data()
    
    analysis_text = f"""
🔍 **AI ANALYSIS STARTED**

📱 **Target APK**: {user_data.get('original_name', 'Unknown')}
📦 **File Size**: {user_data.get('file_size', 0) / (1024*1024):.2f} MB
🎯 **Category**: {user_data.get('selected_category', 'Auto-Detect')}
🤖 **AI Processing**: DeepSeek + WormGPT

**Processing Engines Active:**
✅ Go Analyzer (Static analysis)
✅ Rust Cracker (Binary manipulation) 
✅ C++ Breaker (GPU acceleration)
✅ Java DEX (Android specifics)
✅ Python Bridge (AI integration)

⏱️ **Estimated Time**: 5-15 seconds
⚡ **Speed**: Ultra-fast multi-processing
"""
    
    msg = await message.answer(analysis_text, parse_mode='Markdown')
    await state.update_data(analysis_msg_id=msg.message_id)
    
    # Start async analysis
    asyncio.create_task(perform_dual_ai_analysis(message, state))

async def perform_dual_ai_analysis(message: types.Message, state: FSMContext):
    """Perform analysis with both AI systems"""
    user_data = await state.get_data()
    user_id = message.from_user.id
    
    try:
        # Update status
        await update_analysis_status(message, state, "🚀 Starting analysis...", 10)
        
        # Prepare payload for orchestrator
        async with aiohttp.ClientSession() as session:
            payload = {
                'apk_path': user_data['apk_path'],
                'category': user_data.get('selected_category', 'auto_detect'),
                'subcategory': user_data.get('selected_subcategory', 'auto_detect'),
                'user_id': user_id,
                'use_dual_ai': True,
                'ai_preferences': {
                    'deepseek': True,
                    'wormgpt': True,
                    'combined_analysis': True
                }
            }
            
            await update_analysis_status(message, state, "🤖 Connecting to AI systems...", 30)
            
            async with session.post(f"{ORCHESTRATOR_URL}/analyze", json=payload) as response:
                if response.status == 200:
                    analysis_result = await response.json()
                    
                    await state.update_data(analysis_result=analysis_result)
                    await update_analysis_status(message, state, "✅ AI Analysis Complete!", 100)
                    
                    # Show comprehensive results
                    await show_analysis_results(message, state, analysis_result)
                    
                else:
                    error_text = await response.text()
                    await update_analysis_status(message, state, "❌ Analysis failed!", 0)
                    await message.answer(f"❌ Analysis error: {response.status}\n{error_text}")
    
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        await update_analysis_status(message, state, "❌ Analysis error!", 0)
        await message.answer(f"❌ Error: {str(e)}")

async def update_analysis_status(message: types.Message, state: FSMContext, text: str, progress: int):
    """Update analysis status with progress bar"""
    user_data = await state.get_data()
    msg_id = user_data.get('analysis_msg_id')
    
    if not msg_id:
        return
    
    # Create progress bar
    bar_length = 20
    filled = int(bar_length * progress / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    # Active AI indicator
    if progress < 25:
        ai_status = "🔹 DeepSeek Analyzing..."
    elif progress < 50:
        ai_status = "🔸 WormGPT Processing..."
    elif progress < 75:
        ai_status = "🔹 Multi-Engine Coordination..."
    else:
        ai_status = "🔸 AI Fusion Complete!"
    
    status_text = f"""
🔍 **AI ANALYSIS IN PROGRESS** [{progress}%]

{bar}

{text}

{ai_status}
"""
    
    try:
        await bot.edit_message_text(
            status_text,
            chat_id=message.chat.id,
            message_id=msg_id,
            parse_mode='Markdown'
        )
    except:
        pass  # Message not editable is okay

async def show_analysis_results(message: types.Message, state: FSMContext, analysis_result: Dict):
    """Show comprehensive AI analysis results"""
    
    # Extract key information
    vuln_count = len(analysis_result.get('vulnerabilities', []))
    prot_count = len(analysis_result.get('protections', []))
    rec_count = len(analysis_result.get('recommendations', []))
    security_score = analysis_result.get('security_score', 0)
    ai_confidence = analysis_result.get('ai_confidence', 0.7)
    
    result_text = f"""
🤖 **DUAL AI ANALYSIS COMPLETE**

📊 **ANALYSIS SUMMARY:**
• 🔍 Vulnerabilities Found: {vuln_count}
• 🛡️ Protections Detected: {prot_count}
• 🧠 AI Recommendations: {rec_count}
• 📈 Security Score: {security_score}/100
• 🧠 AI Confidence: {ai_confidence:.2f}

**AI-POWERED INSIGHTS:**
"""
    
    # Add DeepSeek analysis if available
    if 'deepseek_analysis' in analysis_result:
        ds_result = analysis_result['deepseek_analysis']
        ds_vulns = len(ds_result.get('vulnerabilities', []))
        result_text += f"🔹 **DeepSeek AI:** {ds_vulns} vulnerabilities\n"
    
    # Add WormGPT analysis if available
    if 'wormgpt_analysis' in analysis_result:
        wg_result = analysis_result['wormgpt_analysis']
        wg_patterns = len(wg_result.get('crack_patterns', []))
        result_text += f"🔸 **WormGPT AI:** {wg_patterns} crack patterns\n"
    
    result_text += f"""
**CRITICAL FINDINGS:**
"""
    
    # Show top vulnerabilities
    vulnerabilities = analysis_result.get('vulnerabilities', [])
    for i, vuln in enumerate(vulnerabilities[:5], 1):
        result_text += f"{i}. 🔥 **{vuln.get('type', 'Unknown')}** ({vuln.get('severity', 'MEDIUM')})\n"
    
    if len(vulnerabilities) > 5:
        result_text += f"... and {len(vulnerabilities) - 5} more\n"
    
    # Create action keyboard
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🎮 Apply Recommended Fixes", callback_data="apply_fixes"),
        InlineKeyboardButton("🔧 Customize Modifications", callback_data="customize_mods")
    )
    keyboard.add(
        InlineKeyboardButton("🧪 Test Stability", callback_data="test_stability"),
        InlineKeyboardButton("🚀 AI-Enhanced Crack", callback_data="ai_crack")
    )
    keyboard.add(
        InlineKeyboardButton("📊 Detailed Report", callback_data="detailed_report"),
        InlineKeyboardButton("🔄 Re-Analyze", callback_data="reanalyze")
    )
    
    await message.answer(result_text, reply_markup=keyboard, parse_mode='Markdown')
    await CrackStates.CUSTOMIZING_FIXES.set()

# Additional handlers would continue here...

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)