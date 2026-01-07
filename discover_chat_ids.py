#!/usr/bin/env python3
"""
Utility script to discover Telegram Chat IDs.

This script temporarily listens for messages from ANY chat
and displays the chat_id of each sender. Useful for finding
chat IDs when setting up multi-user access.

SECURITY WARNING: 
- Only run this in a controlled environment
- Stop immediately after collecting IDs
- Never deploy with this running

Usage:
    python discover_chat_ids.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv()

# Check if bot token is configured
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
if not bot_token:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN not found in .env")
    print("Please configure your bot token first.")
    sys.exit(1)

print("=" * 70)
print("🔍 TELEGRAM CHAT ID DISCOVERY TOOL")
print("=" * 70)
print()
print("⚠️  SECURITY NOTICE:")
print("   This script accepts messages from ANY chat (no authorization)")
print("   Use ONLY for discovering chat IDs, then stop immediately")
print()
print("📋 INSTRUCTIONS:")
print("   1. Keep this script running")
print("   2. Ask each team member to send a message to your bot")
print("   3. Their chat_id will appear below")
print("   4. Copy the IDs and press Ctrl+C to stop")
print()
print("=" * 70)
print()

# Import here to avoid import errors before env check
import requests
import time

discovered_chats = {}

def get_updates(offset: int = 0) -> list:
    """Get updates from Telegram without filtering."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        params = {
            'offset': offset,
            'timeout': 30,
            'allowed_updates': ['message']
        }
        
        response = requests.get(url, params=params, timeout=35)
        response.raise_for_status()
        
        data = response.json()
        return data.get('result', []) if data.get('ok') else []
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Connection error: {e}")
        return []


def format_user_info(chat: dict) -> str:
    """Format chat information for display."""
    chat_id = chat['id']
    chat_type = chat['type']
    
    if chat_type == 'private':
        first_name = chat.get('first_name', '')
        last_name = chat.get('last_name', '')
        username = chat.get('username', '')
        
        name = f"{first_name} {last_name}".strip() or "Unknown"
        user_handle = f"@{username}" if username else "no username"
        
        return f"👤 {name} ({user_handle})"
    elif chat_type == 'group':
        title = chat.get('title', 'Unknown Group')
        return f"👥 Group: {title}"
    elif chat_type == 'supergroup':
        title = chat.get('title', 'Unknown Supergroup')
        return f"👥 Supergroup: {title}"
    else:
        return f"💬 {chat_type.capitalize()}"


def listen_for_chats():
    """Listen for messages and display chat IDs."""
    print("👂 Listening for messages... (Press Ctrl+C to stop)\n")
    
    offset = 0
    
    try:
        while True:
            updates = get_updates(offset)
            
            for update in updates:
                offset = update['update_id'] + 1
                
                message = update.get('message')
                if not message:
                    continue
                
                chat = message['chat']
                chat_id = str(chat['id'])
                message_text = message.get('text', '(no text)')[:30]
                
                # Track if this is a new chat
                if chat_id not in discovered_chats:
                    discovered_chats[chat_id] = {
                        'info': format_user_info(chat),
                        'count': 0
                    }
                
                discovered_chats[chat_id]['count'] += 1
                
                # Display message
                user_info = discovered_chats[chat_id]['info']
                count = discovered_chats[chat_id]['count']
                
                print(f"📩 Message #{count} from {user_info}")
                print(f"   💬 Text: {message_text}")
                print(f"   🆔 CHAT_ID: {chat_id}")
                print()
    
    except KeyboardInterrupt:
        print("\n")
        print("=" * 70)
        print("🛑 STOPPED - Summary of Discovered Chats")
        print("=" * 70)
        print()
        
        if discovered_chats:
            print("📋 Found Chat IDs:\n")
            
            for chat_id, info in discovered_chats.items():
                print(f"  {info['info']}")
                print(f"  🆔 {chat_id}")
                print(f"  📊 Sent {info['count']} message(s)")
                print()
            
            # Generate .env configuration
            print("=" * 70)
            print("📝 Configuration for .env file:")
            print("=" * 70)
            print()
            
            if len(discovered_chats) == 1:
                chat_id = list(discovered_chats.keys())[0]
                print("# Single user configuration:")
                print(f"TELEGRAM_CHAT_ID={chat_id}")
            else:
                all_ids = ",".join(discovered_chats.keys())
                print("# Multi-user configuration:")
                print(f"TELEGRAM_AUTHORIZED_CHAT_IDS={all_ids}")
            
            print()
            print("=" * 70)
            print("✅ Copy the configuration above to your .env file")
            print("=" * 70)
        else:
            print("❌ No messages received. Make sure:")
            print("   1. Your bot token is correct")
            print("   2. Users sent messages to the bot")
            print("   3. Messages were sent AFTER this script started")


if __name__ == "__main__":
    try:
        listen_for_chats()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
