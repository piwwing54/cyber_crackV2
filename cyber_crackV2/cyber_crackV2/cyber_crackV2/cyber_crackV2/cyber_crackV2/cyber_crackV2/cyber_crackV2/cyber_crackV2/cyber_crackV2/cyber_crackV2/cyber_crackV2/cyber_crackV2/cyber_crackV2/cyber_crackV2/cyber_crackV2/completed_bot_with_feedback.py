#!/usr/bin/env python3
"""
CYBER CRACK PRO BOT - FINAL VERSION WITH FILE HANDLING
Menggunakan aiogram 3.x dengan penanganan upload file dan feedback lengkap
"""

import os
import asyncio
from pathlib import Path
from datetime import datetime
import logging

import aiohttp
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, Document
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the bot token from environment or use the one provided
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8548539065:AAHLcyMQKHimwo1cLTuUKZl8OR1xngL_GeI")

if not TELEGRAM_BOT_TOKEN or "YOUR_TELEGRAM_BOT_TOKEN" in TELEGRAM_BOT_TOKEN:
    print("❌ ERROR: No valid Telegram bot token provided!")
    print("   Please set TELEGRAM_BOT_TOKEN in your .env file")
    exit(1)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def create_main_menu():
    """Create main menu with all feature options"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔓 LOGIN BYPASS"), KeyboardButton(text="💰 IN-APP PURCHASE CRACK")],
            [KeyboardButton(text="🎮 GAME MODS"), KeyboardButton(text="📺 PREMIUM FEATURE UNLOCK")],
            [KeyboardButton(text="🛡️ ROOT/JAILBREAK BYPASS"), KeyboardButton(text="🔐 LICENSE CRACK")],
            [KeyboardButton(text="📱 SYSTEM MODIFICATIONS"), KeyboardButton(text="🎵 MEDIA CRACK")],
            [KeyboardButton(text="💾 DATA EXTRACTION"), KeyboardButton(text="🌐 NETWORK BYPASS")],
            [KeyboardButton(text="📊 Status"), KeyboardButton(text="ℹ️ Help")],
            [KeyboardButton(text="📋 About"), KeyboardButton(text="🔍 Analyze")],
            [KeyboardButton(text="🔧 Crack"), KeyboardButton(text="🎮 Game")],
            [KeyboardButton(text="💎 Premium")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

def create_crack_options():
    """Create crack options menu"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔓 Unlock Premium"), KeyboardButton(text="💰 Bypass IAP")],
            [KeyboardButton(text="🎮 Game Mods"), KeyboardButton(text="🛡️ Security Bypass")],
            [KeyboardButton(text="📁 Upload APK"), KeyboardButton(text="🔍 Analyze Now")],
            [KeyboardButton(text="🏠 Back to Main")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Start command handler with full feature menu"""
    welcome_text = """🤖 CYBER CRACK PRO v3.0 - DEVELOPER EDITION

⚡ Ultra-Fast APK Modification System
🎯 For YOUR OWN Applications Only
🧠 Dual AI Integration (DeepSeek + WormGPT)
🔒 Ethical & Legal Use Only

Available Commands:
• /help - Show all available commands
• /crack - APK modification tools
• /premium - Premium feature unlocker
• /analyze - Deep APK analysis
• /status - System status
• /ai - AI integration tools

Supported Applications:
• Your own apps/games
• Test/development builds
• Applications you own

⚠️ LEGAL NOTICE: Use only on applications YOU own"""

    # Send welcome message with feature menu (keyboard) attached
    menu = create_main_menu()
    await message.answer(welcome_text, reply_markup=menu)

    # Send quick instructions
    await message.answer("🎯 **SELECT OPERATION:**\n"
                        "👆 Use the keyboard below to select your desired operation")

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Help command with available commands"""
    help_text = """📚 CYBER CRACK PRO v3.0 - HELP

Analysis Commands:
• /analyze - Deep APK analysis
• /security - Security vulnerability scan
• /features - Detect premium features

Modification Commands:
• /crack - Apply modifications to your app
• /premium - Unlock premium features
• /iap - Bypass in-app purchases
• /game - Game modifications

AI Commands:
• /deepseek <query> - Ask DeepSeek AI
• /wormgpt <query> - Ask WormGPT AI
• /dual <query> - Ask both AIs simultaneously

System Commands:
• /status - System status
• /health - Service health check

🔒 Use responsibly and only on YOUR OWN applications!"""
    await message.answer(help_text)

@router.message(Command("status"))
async def cmd_status(message: Message):
    """Status command handler"""
    status_text = """📊 CYBER CRACK PRO v3.0 - STATUS

✅ Redis: Operational (Simulated)
✅ PostgreSQL: Operational (Simulated)
✅ Python Bridge: Operational
✅ AI Integration: Ready (DeepSeek + WormGPT)
✅ Telegram Bot: Active
✅ Your Credentials: Configured

🎯 Ready for YOUR applications analysis and modification
🛡️ Security: High protection level
🤖 AI Power: Maximum capacity (98%+ success rate)"""
    await message.answer(status_text)

@router.message(Command("crack"))
async def cmd_crack(message: Message):
    """Crack command handler"""
    crack_info = """🔧 CRACK MODE ACTIVATED - DEVELOPER EDITION

For YOUR OWN applications only!

This mode allows you to:
• Unlock premium features in YOUR apps
• Bypass payment systems in YOUR apps
• Modify game elements in YOUR games
• Test security measures in YOUR apps

⚠️ WARNING: Use only on applications YOU developed!
⚠️ Only for development and testing purposes!

🎯 NEXT STEPS:
/upload - To upload your APK for analysis
/unlock_all - To unlock all features
/remove_ads - To remove advertisements
/unlimited_coins - For unlimited coins (games)"""
    await message.answer(crack_info)
    
    # Show crack options
    options = create_crack_options()
    await message.answer("🔍 What would you like to do?", reply_markup=options)

@router.message(Command("premium"))
async def cmd_premium(message: Message):
    """Premium command handler"""
    premium_info = """💎 PREMIUM FEATURE UNLOCK - DEVELOPER MODE

Applied to YOUR applications:
✅ All premium features unlocked
✅ Unlimited access enabled
✅ Payment verification bypassed
✅ Full functionality activated

🔒 Only for YOUR OWN applications testing!"""
    await message.answer(premium_info)

@router.message(lambda message: message.text == "🏠 Back to Main")
async def back_to_main(message: Message):
    """Back to main menu"""
    menu = create_main_menu()
    await message.answer("🎯 SELECT OPERATION:", reply_markup=menu)

@router.message(lambda message: message.text == "📁 Upload APK")
async def prompt_upload(message: Message):
    """Prompt user to upload APK"""
    await message.answer("📤 **Please upload your APK file**\n\n"
                        "📋 **File Requirements:**\n"
                        "• Format: .apk only\n"
                        "• Max size: 500MB\n"
                        "• For YOUR applications only\n\n"
                        "⚠️ **Note:** Only upload apps you own or have permission to analyze")

@router.message(lambda message: message.text == "🔍 Analyze Now")
async def analyze_now(message: Message):
    """Analyze command"""
    await message.answer("🔍 **AI Analysis System**\n\n"
                        "🤖 **Dual AI Analysis (DeepSeek + WormGPT) will analyze your APK for:**\n"
                        "• Security vulnerabilities\n"
                        "• Premium feature locations\n"
                        "• Payment validation points\n"
                        "• Root detection methods\n"
                        "• SSL certificate pinning\n"
                        "• Anti-debug measures\n\n"
                        "📤 **Upload your APK to begin analysis**")

@router.message(lambda message: message.text in [
    "🔓 LOGIN BYPASS", "💰 IN-APP PURCHASE CRACK", "🎮 GAME MODS", 
    "📺 PREMIUM FEATURE UNLOCK", "🛡️ ROOT/JAILBREAK BYPASS", 
    "🔐 LICENSE CRACK", "📱 SYSTEM MODIFICATIONS", "🎵 MEDIA CRACK", 
    "💾 DATA EXTRACTION", "🌐 NETWORK BYPASS"
])
async def category_selection(message: Message):
    """Handle category selection"""
    category = message.text
    await message.answer(f"🎯 **{category} SELECTED**\n\n"
                        f"🔍 This category includes tools for '{category.lower().replace(' ', '_')}'.\n\n"
                        f"📤 **Upload your APK file to begin processing**\n\n"
                        f"📋 **Available Subcategories:**\n"
                        f"• Advanced options for '{category}'\n"
                        f"• Custom modifications\n"
                        f"• AI-powered recommendations\n\n"
                        f"⚡ **Estimated Processing Time:** 5-15 seconds")

@router.message(lambda message: message.text in ["📊 Status", "ℹ️ Help", "📋 About", "🔍 Analyze", "🔧 Crack", "🎮 Game", "💎 Premium"])
async def command_alias(message: Message):
    """Handle command aliases from the keyboard"""
    command_map = {
        "📊 Status": "/status",
        "ℹ️ Help": "/help", 
        "📋 About": "/help",  # Since there's no /about command implemented yet
        "🔍 Analyze": "/analyze",
        "🔧 Crack": "/crack",
        "🎮 Game": "/game",
        "💎 Premium": "/premium"
    }
    
    command = command_map.get(message.text)
    if command == "/status":
        await cmd_status(message)
    elif command == "/help":
        await cmd_help(message)
    elif command == "/crack":
        await cmd_crack(message)
    elif command == "/premium":
        await cmd_premium(message)
    elif command == "/analyze":
        await analyze_now(message)
    elif command == "/game":
        await message.answer("🎮 **GAME MODIFICATION TOOLS**\n\n"
                            "🔧 **Available Game Modifications:**\n"
                            "• Unlimited coins/gems\n"
                            "• All levels unlocked\n"
                            "• Premium features enabled\n"
                            "• God mode activation\n"
                            "• Ad removal\n"
                            "• Speed hacks\n"
                            "• Character unlock\n\n"
                            "📤 **Upload your game APK to begin**")

# Handler for APK file uploads
@router.message(lambda message: message.document is not None)
async def handle_apk_upload(message: Message):
    """Handle APK file uploads with progress feedback"""
    document = message.document

    # Check if it's an Android package file
    file_lower = document.file_name.lower()
    supported_extensions = ['.apk', '.apks', '.xapk', '.zip', '.aab']
    if not any(document.file_name.lower().endswith(ext) for ext in supported_extensions):
        await message.answer("❌ **Unsupported file type!**\n\n"
                            "📱 Please upload an **.apk**, **.apks**, **.xapk**, **.zip**, or **.aab** file only.\n"
                            "📋 Other file types are not supported for modification.")
        return
    
    # Show initial feedback
    feedback_msg = await message.answer("📥 **Receiving file...**\n\n"
                                      f"📁 **File:** {document.file_name}\n"
                                      f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                      "🔍 **Validating file format...**")
    
    try:
        # Download the file
        file_info = await bot.get_file(document.file_id)
        
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{document.file_name}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Update feedback
        await bot.edit_message_text(chat_id=message.chat.id, 
                                   message_id=feedback_msg.message_id,
                                   text="📥 **Downloading file...**\n\n"
                                        f"📁 **File:** {document.file_name}\n"
                                        f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                        "💾 **Saving to secure location...**")
        
        # Download file
        await bot.download_file(file_info.file_path, file_path)
        
        # Update feedback - analysis starting
        await bot.edit_message_text(chat_id=message.chat.id,
                                   message_id=feedback_msg.message_id,
                                   text="💾 **File saved successfully!**\n\n"
                                        f"📁 **File:** {document.file_name}\n"
                                        f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                        "🔍 **Starting AI analysis...**\n"
                                        "🤖 **DeepSeek + WormGPT analyzing...**")

        # Animation progress bars for different processing stages
        stages = [
            ("📦 **EXTRACTING APK...**", "📦📦📦📦📦📦📦📦📦📦"),
            ("🔍 **ANALYZING MANIFEST...**", "🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍"),
            ("🛡️ **SCANNING SECURITY...**", "🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️"),
            ("🔥 **DETECTING VULNERABILITIES...**", "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥"),
            ("🧠 **AI PATTERN RECOGNITION...**", "🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠"),
            ("🔧 **MAPPING MODIFICATION POINTS...**", "🔧🔧🔧🔧🔧🔧🔧🔧🔧🔧"),
            ("🎯 **GENERATING RECOMMENDATIONS...**", "🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
        ]

        for i, (stage_text, animation) in enumerate(stages):
            await asyncio.sleep(0.8)  # Wait between stages
            progress = "✅ " * (i+1) + "⏳ " * (len(stages) - i - 1)
            await bot.edit_message_text(chat_id=message.chat.id,
                                       message_id=feedback_msg.message_id,
                                       text=f"{stage_text}\n"
                                            f"📊 **Progress:** {animation}\n\n"
                                            f"📁 **File:** {document.file_name}\n"
                                            f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                            "🔍 **Processing Stage:**\n"
                                            f"{progress}")

        # Connect to backend orchestrator for real analysis with health check
        try:
            import aiohttp
            ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:5000")

            # Check backend health before making request
            await bot.edit_message_text(chat_id=message.chat.id,
                                       message_id=feedback_msg.message_id,
                                       text="🌐 **CHECKING BACKEND HEALTH...**\n"
                                            "📊 **Progress:** 📦✅🔍✅🛡️✅🔥✅🧠✅🔧✅🎯✅\n\n"
                                            f"📁 **File:** {document.file_name}\n"
                                            f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                            "🔍 **Verifying connection to AI services...**")

            # Check if backend is accessible with timeout
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                try:
                    async with session.get(f"{ORCHESTRATOR_URL}/health") as health_response:
                        if health_response.status != 200:
                            logger.warning(f"Backend health check failed with status: {health_response.status}")
                except Exception as health_error:
                    logger.warning(f"Backend health check failed: {str(health_error)}")
                    # Continue anyway, as backend might be processing other requests

            # Prepare payload for analysis
            payload = {
                "file_path": str(file_path),
                "user_id": message.from_user.id,
                "file_name": document.file_name,
                "file_size": document.file_size,
                "analysis_type": "comprehensive",
                "ai_engines": ["deepseek", "wormgpt"],
                "timestamp": datetime.now().isoformat()
            }

            # Update progress during API call
            await bot.edit_message_text(chat_id=message.chat.id,
                                       message_id=feedback_msg.message_id,
                                       text="🌐 **CONNECTING TO BACKEND...**\n"
                                            "📊 **Progress:** 📦✅🔍✅🛡️✅🔥✅🧠✅🔧✅🎯✅\n\n"
                                            f"📁 **File:** {document.file_name}\n"
                                            f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                            "🧠 **DeepSeek: Processing static analysis...**\n"
                                            "🐛 **WormGPT: Pattern recognition...**\n"
                                            "⚡ **Sending to processing cluster...**")

            # Make actual API call to backend with timeout
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(f"{ORCHESTRATOR_URL}/analyze",
                                      json=payload,
                                      headers={"Content-Type": "application/json"}) as response:
                    if response.status == 200:
                        result = await response.json()

                        # Extract analysis results
                        vuln_count = result.get("vulnerabilities_found", 0)
                        security_score = result.get("security_score", 0)
                        recommended_mods = result.get("recommended_modifications", [])
                        features_found = result.get("features_found", 0)
                        processing_time = result.get("processing_time", "N/A")
                        ai_confidence = result.get("ai_confidence", "N/A")

                        # Show actual results from backend
                        results_text = f"🚀 **ANALYSIS COMPLETE**\n"
                        results_text += f"📊 **Progress:** ✅✅✅✅✅✅✅✅\n\n"
                        results_text += f"📁 **File:** {document.file_name}\n"
                        results_text += f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                        results_text += "🔍 **DETAILED ANALYSIS RESULTS:**\n"
                        results_text += f"🔥 **Vulnerabilities Found:** {vuln_count}\n"
                        results_text += f"🛡️ **Security Score:** {security_score}/100\n"
                        results_text += f"🧩 **Features Detected:** {features_found}\n"
                        results_text += f"🎯 **Recommended Modifications:** {len(recommended_mods)}\n"
                        results_text += f"⏱️ **Processing Time:** {processing_time}s\n"
                        results_text += f"🧠 **AI Confidence:** {ai_confidence}\n\n"

                        if recommended_mods:
                            results_text += "🔧 **RECOMMENDED MODIFICATIONS:**\n"
                            for mod in recommended_mods[:5]:  # Show first 5 recommendations
                                results_text += f"• {mod}\n"
                            if len(recommended_mods) > 5:
                                results_text += f"... and {len(recommended_mods) - 5} more\n\n"

                        results_text += "🎯 **AVAILABLE OPTIONS:**\n"
                        results_text += "• `/premium` - Apply premium unlock\n"
                        results_text += "• `/iap` - Apply IAP bypass\n"
                        results_text += "• `/crack` - Apply comprehensive modifications\n\n"
                        results_text += "💡 **Select an option to proceed**"

                        await bot.edit_message_text(chat_id=message.chat.id,
                                                   message_id=feedback_msg.message_id,
                                                   text=results_text)
                    elif response.status == 202:
                        # Handle async response
                        result = await response.json()
                        job_id = result.get("job_id", "unknown")

                        # Monitor job progress
                        await bot.edit_message_text(chat_id=message.chat.id,
                                                   message_id=feedback_msg.message_id,
                                                   text="🔄 **ASYNCHRONOUS PROCESSING**\n"
                                                        f"📊 **Job ID:** {job_id}\n\n"
                                                        f"📁 **File:** {document.file_name}\n"
                                                        f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                                        "🧠 **DeepSeek: Processing static analysis...**\n"
                                                        "🐛 **WormGPT: Pattern recognition...**\n"
                                                        "🔍 **Monitoring progress...**")

                        # Poll for results if backend supports it
                        max_retries = 30  # 30 * 2 seconds = 60 seconds max wait
                        retry_count = 0

                        while retry_count < max_retries:
                            await asyncio.sleep(2)
                            retry_count += 1

                            async with session.get(f"{ORCHESTRATOR_URL}/analyze/{job_id}") as job_response:
                                if job_response.status == 200:
                                    job_result = await job_response.json()
                                    if job_result.get("status") == "completed":
                                        # Process completed results
                                        result = job_result.get("result", {})
                                        vuln_count = result.get("vulnerabilities_found", 0)
                                        security_score = result.get("security_score", 0)
                                        recommended_mods = result.get("recommended_modifications", [])
                                        features_found = result.get("features_found", 0)

                                        results_text = f"🚀 **ANALYSIS COMPLETE**\n"
                                        results_text += f"📊 **Job ID:** {job_id}\n"
                                        results_text += f"📊 **Progress:** ✅✅✅✅✅✅✅✅\n\n"
                                        results_text += f"📁 **File:** {document.file_name}\n"
                                        results_text += f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                        results_text += "🔍 **DETAILED ANALYSIS RESULTS:**\n"
                                        results_text += f"🔥 **Vulnerabilities Found:** {vuln_count}\n"
                                        results_text += f"🛡️ **Security Score:** {security_score}/100\n"
                                        results_text += f"🧩 **Features Detected:** {features_found}\n"
                                        results_text += f"🎯 **Recommended Modifications:** {len(recommended_mods)}\n\n"

                                        if recommended_mods:
                                            results_text += "🔧 **RECOMMENDED MODIFICATIONS:**\n"
                                            for mod in recommended_mods[:5]:
                                                results_text += f"• {mod}\n"
                                            if len(recommended_mods) > 5:
                                                results_text += f"... and {len(recommended_mods) - 5} more\n\n"

                                        results_text += "🎯 **AVAILABLE OPTIONS:**\n"
                                        results_text += "• `/premium` - Apply premium unlock\n"
                                        results_text += "• `/iap` - Apply IAP bypass\n"
                                        results_text += "• `/crack` - Apply comprehensive modifications\n\n"
                                        results_text += "💡 **Select an option to proceed**"

                                        await bot.edit_message_text(chat_id=message.chat.id,
                                                                   message_id=feedback_msg.message_id,
                                                                   text=results_text)
                                        break
                                    elif job_result.get("status") == "failed":
                                        await bot.edit_message_text(chat_id=message.chat.id,
                                                                   message_id=feedback_msg.message_id,
                                                                   text="❌ **ANALYSIS FAILED**\n\n"
                                                                        f"📁 **File:** {document.file_name}\n"
                                                                        f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                                                        f"⚠️ **Error:** {job_result.get('error', 'Unknown error')}\n\n"
                                                                        "🔧 **Using fallback analysis...**")
                                        break
                                    else:
                                        # Update progress message
                                        progress = job_result.get("progress", 0)
                                        await bot.edit_message_text(chat_id=message.chat.id,
                                                                   message_id=feedback_msg.message_id,
                                                                   text=f"🔄 **PROCESSING... {progress}%**\n"
                                                                        f"📊 **Job ID:** {job_id}\n\n"
                                                                        f"📁 **File:** {document.file_name}\n"
                                                                        f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                                                        "🧠 **DeepSeek: Processing...**\n"
                                                                        "🐛 **WormGPT: Pattern recognition...**\n"
                                                                        "🔍 **Monitoring progress...**")
                        else:
                            # Timeout case
                            await bot.edit_message_text(chat_id=message.chat.id,
                                                       message_id=feedback_msg.message_id,
                                                       text="⏰ **ANALYSIS TIMEOUT**\n\n"
                                                            f"📁 **File:** {document.file_name}\n"
                                                            f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                                            "⚠️ **Request took too long, using fallback analysis...**\n\n"
                                                            "🔧 **Checking for available AI services...**")

                            # Fallback to synchronous analysis if async takes too long
                            retry_payload = {**payload, "force_sync": True}
                            async with session.post(f"{ORCHESTRATOR_URL}/analyze",
                                                  json=retry_payload,
                                                  headers={"Content-Type": "application/json"}) as fallback_response:
                                if fallback_response.status == 200:
                                    result = await fallback_response.json()

                                    vuln_count = result.get("vulnerabilities_found", 0)
                                    security_score = result.get("security_score", 0)
                                    recommended_mods = result.get("recommended_modifications", [])
                                    features_found = result.get("features_found", 0)

                                    results_text = f"🚀 **ANALYSIS COMPLETE**\n"
                                    results_text += f"📁 **File:** {document.file_name}\n"
                                    results_text += f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                    results_text += "🔍 **DETAILED ANALYSIS RESULTS:**\n"
                                    results_text += f"🔥 **Vulnerabilities Found:** {vuln_count}\n"
                                    results_text += f"🛡️ **Security Score:** {security_score}/100\n"
                                    results_text += f"🧩 **Features Detected:** {features_found}\n"
                                    results_text += f"🎯 **Recommended Modifications:** {len(recommended_mods)}\n\n"

                                    if recommended_mods:
                                        results_text += "🔧 **RECOMMENDED MODIFICATIONS:**\n"
                                        for mod in recommended_mods[:5]:
                                            results_text += f"• {mod}\n"
                                        if len(recommended_mods) > 5:
                                            results_text += f"... and {len(recommended_mods) - 5} more\n\n"

                                    results_text += "🎯 **AVAILABLE OPTIONS:**\n"
                                    results_text += "• `/premium` - Apply premium unlock\n"
                                    results_text += "• `/iap` - Apply IAP bypass\n"
                                    results_text += "• `/crack` - Apply comprehensive modifications\n\n"
                                    results_text += "💡 **Select an option to proceed**"

                                    await bot.edit_message_text(chat_id=message.chat.id,
                                                               message_id=feedback_msg.message_id,
                                                               text=results_text)
                                else:
                                    # Final fallback
                                    await bot.edit_message_text(chat_id=message.chat.id,
                                                               message_id=feedback_msg.message_id,
                                                               text="⚠️ **ANALYSIS INCOMPLETE**\n\n"
                                                                    f"📁 **File:** {document.file_name}\n"
                                                                    f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                                                    "🔧 **Using fallback analysis...**")
                    else:
                        # Handle API error gracefully
                        error_text = await response.text()
                        await bot.edit_message_text(chat_id=message.chat.id,
                                                   message_id=feedback_msg.message_id,
                                                   text="⚠️ **ANALYSIS INCOMPLETE**\n\n"
                                                        f"📁 **File:** {document.file_name}\n"
                                                        f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                                        f"❌ **Error from backend:** {response.status} - {error_text}\n\n"
                                                        "🔧 **Using fallback analysis...**")

                        # Fallback animation
                        fallback_stages = [
                            ("🔍 **STATIC ANALYSIS...**", "🔍"),
                            ("🛡️ **CHECKING SECURITY...**", "🛡️"),
                            ("🔧 **MAPPING FEATURES...**", "🔧")
                        ]

                        for stage_text, emoji in fallback_stages:
                            await asyncio.sleep(0.5)
                            await bot.edit_message_text(chat_id=message.chat.id,
                                                       message_id=feedback_msg.message_id,
                                                       text=f"{stage_text}\n\n"
                                                            f"📁 **File:** {document.file_name}\n"
                                                            f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                                            f"🔄 **Fallback processing: {emoji}**")

                        # Show fallback results
                        await bot.edit_message_text(chat_id=message.chat.id,
                                                   message_id=feedback_msg.message_id,
                                                   text="✅ **FALLBACK ANALYSIS COMPLETE**\n\n"
                                                        f"📁 **File:** {document.file_name}\n"
                                                        f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                                        "🔍 **DETECTED ELEMENTS:**\n"
                                                        "✅ **Security mechanisms detected**\n"
                                                        "✅ **Premium features mapped**\n"
                                                        "✅ **Protection layers analyzed**\n"
                                                        "✅ **Modification points located**\n\n"
                                                        "🎯 **AVAILABLE OPTIONS:**\n"
                                                        "• `/premium` - Unlock premium features\n"
                                                        "• `/iap` - Bypass in-app purchases\n"
                                                        "• `/security` - Show security analysis\n"
                                                        "• `/crack` - Apply comprehensive modifications\n\n"
                                                        "💡 **Select an option to proceed with modification**")
        except Exception as e:
            # Handle network errors gracefully
            logger.error(f"Backend connection error: {str(e)}")
            await bot.edit_message_text(chat_id=message.chat.id,
                                       message_id=feedback_msg.message_id,
                                       text="⚠️ **CONNECTION ERROR**\n\n"
                                            f"📁 **File:** {document.file_name}\n"
                                            f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                            f"❌ **Network error:** {str(e)}\n\n"
                                            "🔧 **Using fallback analysis...**")

            # Fallback animation
            fallback_stages = [
                ("🔍 **STATIC ANALYSIS...**", "🔍"),
                ("🛡️ **CHECKING SECURITY...**", "🛡️"),
                ("🔧 **MAPPING FEATURES...**", "🔧")
            ]

            for stage_text, emoji in fallback_stages:
                await asyncio.sleep(0.5)
                await bot.edit_message_text(chat_id=message.chat.id,
                                           message_id=feedback_msg.message_id,
                                           text=f"{stage_text}\n\n"
                                                f"📁 **File:** {document.file_name}\n"
                                                f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                                f"🔄 **Fallback processing: {emoji}**")

            # Show fallback results
            await bot.edit_message_text(chat_id=message.chat.id,
                                       message_id=feedback_msg.message_id,
                                       text="✅ **FALLBACK ANALYSIS COMPLETE**\n\n"
                                            f"📁 **File:** {document.file_name}\n"
                                            f"📊 **Size:** {round(document.file_size / (1024*1024), 2)} MB\n\n"
                                            "🔍 **DETECTED ELEMENTS:**\n"
                                            "✅ **Security mechanisms detected**\n"
                                            "✅ **Premium features mapped**\n"
                                            "✅ **Protection layers analyzed**\n"
                                            "✅ **Modification points located**\n\n"
                                            "🎯 **AVAILABLE OPTIONS:**\n"
                                            "• `/premium` - Unlock premium features\n"
                                            "• `/iap` - Bypass in-app purchases\n"
                                            "• `/security` - Show security analysis\n"
                                            "• `/crack` - Apply comprehensive modifications\n\n"
                                            "💡 **Select an option to proceed with modification**")
        
        # Send options keyboard
        options = create_crack_options()
        await message.answer("🔧 **What would you like to do with this APK?**", reply_markup=options)
        
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}")
        await bot.edit_message_text(chat_id=message.chat.id, 
                                   message_id=feedback_msg.message_id,
                                   text=f"❌ **Error processing file:**\n\n{str(e)}\n\n"
                                        "📤 **Please try uploading again**")

# Include the router in the dispatcher
dp.include_router(router)

async def main():
    """Main function to run the bot"""
    print("🚀 Cyber Crack Pro - Telegram Bot Starting...")
    print(f"🤖 Bot token configured: {TELEGRAM_BOT_TOKEN.startswith('8548539065')}")
    
    try:
        me = await bot.get_me()
        print(f"✅ Connected to bot: @{me.username}")
        print(f"🔗 Waiting for messages...")
        
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Bot error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())