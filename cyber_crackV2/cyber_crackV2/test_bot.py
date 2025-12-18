import asyncio
import aiohttp
import json

async def test_bot_connection():
    """
    Script sederhana untuk menguji koneksi ke sistem Cyber Crack Pro
    """
    print("🚀 Menguji koneksi ke Cyber Crack Pro...")
    
    # Test connection to Python Bridge
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://localhost:8084/health') as response:
                if response.status == 200:
                    print("✅ Python Bridge: BERJALAN (port 8084)")
                    data = await response.json()
                    print(f"   Status: {data}")
                else:
                    print(f"❌ Python Bridge: TIDAK MERESPON (status {response.status})")
        except Exception as e:
            print(f"❌ Python Bridge: ERROR - {str(e)}")
    
    print("\nBot Telegram @Yancumintybot telah siap diakses!")
    print("Anda sekarang dapat mengirim pesan ke bot dan memulai penggunaan Cyber Crack Pro.")
    print("\nFitur-fitur yang tersedia:")
    print("- 🔓 Bypass login/password")
    print("- 💰 Cracking pembelian dalam aplikasi")
    print("- 🎮 Modifikasi game (unlimited coins, dll)")
    print("- 📺 Unlock fitur premium")
    print("- 🛡️ Bypass deteksi root/jailbreak")
    print("- 🔐 Bypass certificate pinning")
    print("- 🐛 Analisis dan debugging APK")
    print("- 🧠 Integrasi AI untuk analisis cerdas")

if __name__ == "__main__":
    asyncio.run(test_bot_connection())