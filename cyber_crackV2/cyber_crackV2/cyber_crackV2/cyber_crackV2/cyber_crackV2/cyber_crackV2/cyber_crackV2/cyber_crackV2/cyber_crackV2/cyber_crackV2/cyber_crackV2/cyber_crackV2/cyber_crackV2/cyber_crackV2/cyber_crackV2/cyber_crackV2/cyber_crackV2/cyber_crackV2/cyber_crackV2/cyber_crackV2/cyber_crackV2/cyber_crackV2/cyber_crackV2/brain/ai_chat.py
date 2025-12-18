#!/usr/bin/env python3
"""
🤖 CYBER CRACK PRO - AI Chat Interface
Direct chat interface with both DeepSeek and WormGPT APIs
"""

import asyncio
import json
import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import aiohttp
from datetime import datetime

# Configure API keys
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
WORMGPT_API_KEY = os.getenv("WORMGPT_API_KEY")
WORMGPT_URL = "https://camillecyrm.serv00.net/Deep.php"

class AIChatInterface:
    """Interface for chatting with both AIs"""
    
    def __init__(self):
        self.session = None
        self.wormgpt_chat_id = None  # Maintain conversation state
        self.deepseek_conversation_history = []
        self.wormgpt_conversation_history = []
        
    async def initialize(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120)
        )
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def chat_with_deepseek(self, message: str, system_prompt: str = None) -> Dict[str, Any]:
        """Chat with DeepSeek API"""
        if not DEEPSEEK_API_KEY:
            return {
                "success": False,
                "error": "DeepSeek API key not configured",
                "reply": "DeepSeek API key is required for this feature"
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history
            messages.extend(self.deepseek_conversation_history)
            messages.append({"role": "user", "content": message})
            
            payload = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2048
            }
            
            async with self.session.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    reply = result["choices"][0]["message"]["content"]
                    
                    # Add to conversation history
                    self.deepseek_conversation_history.append({"role": "user", "content": message})
                    self.deepseek_conversation_history.append({"role": "assistant", "content": reply})
                    
                    # Keep only last 10 exchanges to prevent history from growing too large
                    if len(self.deepseek_conversation_history) > 20:
                        self.deepseek_conversation_history = self.deepseek_conversation_history[-20:]
                    
                    return {
                        "success": True,
                        "reply": reply,
                        "provider": "deepseek",
                        "confidence": 0.8  # Assuming high confidence for valid API response
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"DeepSeek API error {response.status}: {error_text}",
                        "reply": f"DeepSeek API error: {response.status}"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "reply": f"DeepSeek API connection error: {str(e)}"
            }
    
    async def chat_with_wormgpt(self, message: str, mode: str = "chat") -> Dict[str, Any]:
        """Chat with WormGPT API"""
        if not WORMGPT_API_KEY:
            return {
                "success": False,
                "error": "WormGPT API key not configured",
                "reply": "WormGPT API key is required for this feature"
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {WORMGPT_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Based on the API specification provided:
            # For new conversation: POST with "text" field
            # For existing conversation: POST with "chat" and "text" fields
            if self.wormgpt_chat_id:
                # Continue existing conversation
                payload = {
                    "chat": self.wormgpt_chat_id,
                    "text": message
                }
            else:
                # Start new conversation
                payload = {
                    "text": message
                }
            
            async with self.session.post(WORMGPT_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get("status") == "success":
                        reply = result.get("reply", result.get("response", "No response received"))
                        
                        # Store chat ID for continued conversation
                        if "chat_id" in result and not self.wormgpt_chat_id:
                            self.wormgpt_chat_id = result["chat_id"]
                        
                        # Add to conversation history
                        self.wormgpt_conversation_history.append({"role": "user", "content": message})
                        self.wormgpt_conversation_history.append({"role": "assistant", "content": reply})
                        
                        return {
                            "success": True,
                            "reply": reply,
                            "provider": "wormgpt",
                            "chat_id": self.wormgpt_chat_id,
                            "confidence": 0.75
                        }
                    else:
                        error_msg = result.get("error", result.get("message", "Unknown API error"))
                        return {
                            "success": False,
                            "error": f"WormGPT API error: {error_msg}",
                            "reply": f"WormGPT API error: {error_msg}"
                        }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"WormGPT API error {response.status}: {error_text}",
                        "reply": f"WormGPT API error: {response.status}"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "reply": f"WormGPT API connection error: {str(e)}"
            }
    
    async def multi_ai_conversation(self, message: str, purpose: str = "general") -> Dict[str, Any]:
        """Have conversation with both AIs simultaneously"""
        
        # Prepare system prompts based on purpose
        system_prompts = {
            "general": "You are a helpful assistant.",
            "security": "You are an expert Android security analyst.",
            "cracking": "You are an expert APK cracker and modifier.",
            "game_mods": "You specialize in game modification and cheating techniques.",
            "analysis": "Provide detailed technical analysis and code modifications."
        }
        
        system_prompt = system_prompts.get(purpose, "You are a helpful assistant.")
        
        # Run both AIs concurrently
        deepseek_task = self.chat_with_deepseek(message, system_prompt)
        wormgpt_task = self.chat_with_wormgpt(message, "chat")
        
        ds_result, wg_result = await asyncio.gather(
            deepseek_task, 
            wormgpt_task, 
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(ds_result, Exception):
            ds_result = {"success": False, "error": str(ds_result), "reply": "DeepSeek error occurred"}
        
        if isinstance(wg_result, Exception):
            wg_result = {"success": False, "error": str(wg_result), "reply": "WormGPT error occurred"}
        
        # Combine results
        combined_result = {
            "message": message,
            "deepseek_response": ds_result,
            "wormgpt_response": wg_result,
            "conversation_mode": "dual_ai",
            "timestamp": datetime.now().isoformat(),
            "consensus_level": self._calculate_consensus(ds_result, wg_result)
        }
        
        return combined_result
    
    def _calculate_consensus(self, ds_result: Dict, wg_result: Dict) -> str:
        """Calculate consensus level between AIs"""
        if not ds_result["success"] or not wg_result["success"]:
            return "no_consensus"
        
        # Simple similarity check on response length and keywords
        try:
            ds_reply = ds_result.get("reply", "").lower()
            wg_reply = wg_result.get("reply", "").lower()
            
            # Check for similar response patterns
            ds_words = set(ds_reply.split()[:20])  # First 20 words
            wg_words = set(wg_reply.split()[:20])  # First 20 words
            
            # Calculate intersection
            common_words = ds_words.intersection(wg_words)
            consensus_score = len(common_words) / max(len(ds_words), len(wg_words), 1)
            
            if consensus_score >= 0.6:
                return "high"
            elif consensus_score >= 0.3:
                return "medium"
            else:
                return "low"
        
        except:
            return "unknown"
    
    async def reset_conversations(self):
        """Reset all conversation histories"""
        self.deepseek_conversation_history = []
        self.wormgpt_conversation_history = []
        self.wormgpt_chat_id = None
        return {"success": True, "message": "Conversation histories cleared"}
    
    def get_conversation_stats(self) -> Dict[str, int]:
        """Get conversation statistics"""
        return {
            "deepseek_exchanges": len(self.deepseek_conversation_history) // 2,
            "wormgpt_exchanges": len(self.wormgpt_conversation_history) // 2,
            "current_wormgpt_chat_id": self.wormgpt_chat_id,
            "total_messages": len(self.deepseek_conversation_history) + len(self.wormgpt_conversation_history)
        }

# Global instance
ai_chatter = AIChatInterface()

async def main():
    """Test AI chat functionality"""
    import sys
    
    await ai_chatter.initialize()
    
    if len(sys.argv) < 2:
        print("Usage: python ai_chat.py <command> [options]")
        print("Commands: test-deepseek, test-wormgpt, dual-chat, start-chat, continue-chat <message>, reset")
        return
    
    command = sys.argv[1]
    
    try:
        if command == "test-deepseek":
            result = await ai_chatter.chat_with_deepseek("Hello, who are you?")
            print(f"DeepSeek: {result}")
        
        elif command == "test-wormgpt":
            result = await ai_chatter.chat_with_wormgpt("Hello, who are you?")
            print(f"WormGPT: {result}")
        
        elif command == "dual-chat":
            if len(sys.argv) < 3:
                message = "What are you capable of?"
            else:
                message = " ".join(sys.argv[2:])
            
            result = await ai_chatter.multi_ai_conversation(message, "general")
            print("🌐 DUAL AI CONVERSATION RESULT:")
            print(f"DeepSeek: {result['deepseek_response'].get('reply', 'ERROR')[:200]}...")
            print(f"WormGPT: {result['wormgpt_response'].get('reply', 'ERROR')[:200]}...")
            print(f"Consensus: {result['consensus_level']}")
        
        elif command == "start-chat":
            if len(sys.argv) < 3:
                print("Please provide initial message")
                return
            
            message = " ".join(sys.argv[2:])
            result = await ai_chatter.multi_ai_conversation(message, "general")
            print("Chat started with dual AI:")
            print(f"DS: {result['deepseek_response'].get('reply', 'ERROR')}")
            print(f"WG: {result['wormgpt_response'].get('reply', 'ERROR')}")
        
        elif command == "continue-chat":
            if len(sys.argv) < 3:
                print("Please provide message to continue chat")
                return
            
            message = " ".join(sys.argv[2:])
            if ai_chatter.wormgpt_chat_id:
                # Continue WormGPT conversation
                wg_result = await ai_chatter.chat_with_wormgpt(message, "chat")
            else:
                print("No active WormGPT chat session. Run 'start-chat' first.")
                return
            
            # Get DeepSeek response separately
            ds_result = await ai_chatter.chat_with_deepseek(message)
            
            print(f"DS Response: {ds_result.get('reply', 'ERROR')}")
            print(f"WG Response: {wg_result.get('reply', 'ERROR')}")
        
        elif command == "reset":
            result = await ai_chatter.reset_conversations()
            print(f"Conversations reset: {result}")
        
        elif command == "stats":
            stats = ai_chatter.get_conversation_stats()
            print("Conversation Statistics:")
            print(f"  DeepSeek exchanges: {stats['deepseek_exchanges']}")
            print(f"  WormGPT exchanges: {stats['wormgpt_exchanges']}")
            print(f"  Current WormGPT chat ID: {stats['current_wormgpt_chat_id']}")
            print(f"  Total messages: {stats['total_messages']}")
        
        else:
            print(f"Unknown command: {command}")
    
    finally:
        await ai_chatter.close()

if __name__ == "__main__":
    # Add this to system for AI chat functionality
    print("🤖 AI Chat Interface Ready!")
    print("   • DeepSeek API: Configurable via DEEPSEEK_API_KEY")
    print("   • WormGPT API: Configurable via WORMGPT_API_KEY") 
    print("   • Dual AI conversations: Possible")
    print("   • Conversation history: Maintained")
    asyncio.run(main())