async def send_to_backend_fixed(apk_path: str, user_id: int, file_name: str, file_size: int, operation: str = "analyze"):
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
