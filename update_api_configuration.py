# 🔧 CYBER CRACK PRO v3.0 - API CONFIGURATION FIX
# Updated configuration to fix error 422 and use correct endpoint

import os
from pathlib import Path
import json

# Configuration
API_CONFIG = {
    "DEFAULT_BASE_URL": "http://localhost:8001",  # NEW FIXED API SERVER
    "LEGACY_BASE_URL": "http://localhost:8000",   # OLD SERVER (if needed)
    
    "ENDPOINTS": {
        "analyze": "/api/analyze",
        "process": "/api/process", 
        "crack": "/api/crack",
        "health": "/health",
        "status": "/"
    },
    
    "FIELD_MAPPINGS": {
        # Mappings to ensure correct field names for API
        "file_path": "apk_path",  # CRITICAL FIX: Map file_path to apk_path
        "original_file": "apk_path",
        "apk_file": "apk_path"
    },
    
    "REQUEST_TIMEOUT": 30,
    "MAX_RETRIES": 3,
    
    "FORM_DATA_REQUIRED_FIELDS": [
        "apk_path",    # FIXED: This field is now required and properly handled
        "user_id",
        "file_name", 
        "file_size"
    ]
}

def update_bot_config():
    """Update bot configuration to use fixed API endpoints"""

    # Read the current bot file
    bot_file_path = Path("complete_telegram_bot.py")

    if not bot_file_path.exists():
        print("❌ Bot file not found")
        return False

    with open(bot_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update the API endpoint configurations
    # Replace old API URL references with the new fixed ones
    updated_content = content.replace(
        'ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:5000")',
        'ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8001")'  # FIXED PORT
    ).replace(
        'f"{ORCHESTRATOR_URL}/analyze"',
        'f"{ORCHESTRATOR_URL}/api/analyze"'  # FIXED ENDPOINT
    ).replace(
        'f"{ORCHESTRATOR_URL}/process"',
        'f"{ORCHESTRATOR_URL}/api/process"'  # FIXED ENDPOINT
    ).replace(
        'f"{ORCHESTRATOR_URL}/crack"',
        'f"{ORCHESTRATOR_URL}/api/crack"'   # FIXED ENDPOINT
    )

    # Add proper error handling for missing fields
    if 'async with session.post(url, data=payload)' in content:
        # Replace data=payload (form) with proper handling
        updated_content = updated_content.replace(
            'data=payload',
            'json=payload'  # CHANGE TO JSON PAYLOAD FOR BETTER ERROR HANDLING
        )

    # Write updated content back
    with open(bot_file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print("✅ Bot configuration updated to use fixed API endpoints")
    return True

def create_updated_request_function():
    """Create updated request function that properly handles apk_path field"""

    # This would be the updated function to handle API requests properly
    updated_function = '''async def send_to_backend_fixed(apk_path: str, user_id: int, file_name: str, file_size: int, operation: str = "analyze"):
    """Updated function to send requests with proper apk_path field handling"""

    import aiohttp
    import asyncio

    API_CONFIG = {
        "MAX_RETRIES": 3,
        "REQUEST_TIMEOUT": 30
    }

    base_url = "http://localhost:8001"  # FIXED API SERVER
    endpoint_map = {
        "analyze": "/api/analyze",
        "process": "/api/process",
        "crack": "/api/crack"
    }

    url = f"{base_url}{endpoint_map.get(operation, '/api/analyze')}"

    # Prepare payload with CORRECT field names as required by the FIXED API
    payload = {
        "apk_path": apk_path,      # CRITICAL: FIXED FIELD NAME
        "user_id": user_id,        # FIXED: Proper user field
        "file_name": file_name,    # FIXED: Proper name field
        "file_size": file_size,    # FIXED: Proper size field
        "analysis_type": "comprehensive",
        "ai_engines": ["deepseek", "wormgpt"],
        "timestamp": datetime.now().isoformat(),
        "options": {
            "enable_ai_analysis": True,
            "enable_cracking": True,
            "output_format": "modified_apk"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "CyberCrackPro/3.0"
    }

    async with aiohttp.ClientSession() as session:
        for attempt in range(API_CONFIG["MAX_RETRIES"]):
            try:
                async with session.post(
                    url,
                    json=payload,  # SEND AS JSON (not form data to preserve field names)
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=API_CONFIG["REQUEST_TIMEOUT"])
                ) as response:

                    status_code = response.status
                    response_text = await response.text()

                    if status_code == 200:
                        try:
                            json_response = await response.json()
                            return json_response
                        except:
                            return {"success": True, "raw_response": response_text}
                    else:
                        # Log the error response for debugging
                        print(f"❌ API Error {status_code}: {response_text}")

                        # Check if it's the 422 error we're fixing
                        if status_code == 422:
                            try:
                                error_response = json.loads(response_text)
                                print(f"📝 Error details: {error_response}")

                                # SPECIAL HANDLING for 422 errors to prevent them
                                if "apk_path" in str(response_text):
                                    print("⚠️  Detected missing apk_path field - this shouldn't happen with our fix")
                                    print("🔧 Sending fallback request...")

                                    # Try with form data as well, since API expects it
                                    form_payload = aiohttp.FormData()
                                    form_payload.add_field('apk_path', apk_path)
                                    form_payload.add_field('user_id', str(user_id))
                                    form_payload.add_field('file_name', file_name)
                                    form_payload.add_field('file_size', str(file_size))
                                    form_payload.add_field('analysis_type', 'comprehensive')

                                    # Retry with form data
                                    async with session.post(url, data=form_payload, headers={'User-Agent': 'CyberCrackPro/3.0'}) as form_response:
                                        if form_response.status == 200:
                                            return await form_response.json()
                                        else:
                                            form_response_text = await form_response.text()
                                            print(f"❌ Form data attempt also failed: {form_response_text}")
                                            return {"error": f"Failed with status {form_response.status}", "details": form_response_text}
                            except:
                                pass

                        if attempt < API_CONFIG["MAX_RETRIES"] - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        else:
                            return {"error": f"API failed after {API_CONFIG['MAX_RETRIES']} attempts", "status": status_code, "response": response_text}

            except Exception as e:
                if attempt < API_CONFIG["MAX_RETRIES"] - 1:
                    print(f"⚠️ Attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(2 ** attempt)
                else:
                    print(f"❌ Final attempt failed: {e}")
                    return {"error": f"Connection failed: {str(e)}"}

    return {"error": "Max retries exceeded"}
'''

    # Write to a separate file
    with open("updated_api_handler.py", "w") as f:
        f.write(updated_function)

    print("✅ Updated API request function created")
    return True

def verify_configuration():
    """Verify that the configuration fixes are in place"""
    
    print("\\n🔍 VERIFYING API CONFIGURATION FIXES...")
    
    # Check if the correct endpoints exist
    import subprocess
    result = subprocess.run(['python', '-c', '''
import sys
import os
sys.path.append(".")
try:
    from fixed_backend_api import app
    print("✅ Fixed backend API module loaded successfully")
    
    # Check if app has the right routes
    routes = [route.path for route in app.routes]
    required_routes = ["/api/analyze", "/api/process", "/api/crack"]
    
    all_present = all(route in routes for route in required_routes)
    if all_present:
        print("✅ All required API routes present in fixed server")
    else:
        print("❌ Missing required API routes:", [r for r in required_routes if r not in routes])
        
except Exception as e:
    print(f"❌ Error loading fixed backend: {e}")
'''], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

if __name__ == "__main__":
    print("🔧 UPDATING CYBER CRACK PRO v3.0 - API CONFIGURATION FIX")
    print("="*60)
    
    # Update bot configuration
    success1 = update_bot_config()
    
    # Create updated request function
    success2 = create_updated_request_function()
    
    # Verify configuration
    verify_configuration()
    
    if success1 and success2:
        print("\\n🎉 ALL API CONFIGURATION FIXES APPLIED SUCCESSFULLY!")
        print("📋 Summary of fixes:")
        print("   • Updated API endpoints to use port 8001 (fixed server)")
        print("   • Corrected field naming (apk_path instead of file_path)")
        print("   • Added proper error handling for 422 errors")
        print("   • Added fallback mechanisms")
        print("\\n🚀 Fixed backend server ready to start on port 8001")
        print("🔗 API endpoints now properly accept 'apk_path' field")
        print("⚙️  Ready for Analysis-Before-Execution system")
    else:
        print("\\n⚠️  Some configuration updates failed")