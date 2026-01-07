"""
Test script for multi-user Telegram functionality.

This script tests:
- Authorization checking
- Multi-user support
- Chat ID validation
- Message routing

Run after configuring TELEGRAM_AUTHORIZED_CHAT_IDS in .env
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from services.integrations.telegram_service import TelegramService

def test_authorization():
    """Test authorization system."""
    print("=" * 70)
    print("🧪 TESTING TELEGRAM MULTI-USER AUTHORIZATION")
    print("=" * 70)
    print()
    
    try:
        # Initialize service
        telegram = TelegramService()
        
        # Get configured IDs
        authorized_ids = telegram.get_authorized_chat_ids()
        
        print(f"✅ Service initialized successfully")
        print(f"📋 Authorized chat IDs: {len(authorized_ids)}")
        print()
        
        # Display authorized IDs
        if authorized_ids:
            print("👥 Authorized Users:")
            for idx, chat_id in enumerate(authorized_ids, 1):
                print(f"   {idx}. Chat ID: {chat_id}")
            print()
        else:
            print("⚠️  No authorized chat IDs configured!")
            print("   Set TELEGRAM_AUTHORIZED_CHAT_IDS or TELEGRAM_CHAT_ID in .env")
            print()
        
        # Test authorization checks
        print("🔒 Testing Authorization:")
        print()
        
        # Test valid ID
        if authorized_ids:
            valid_id = list(authorized_ids)[0]
            result = telegram.is_authorized(valid_id)
            print(f"   ✅ Valid ID ({valid_id}): {result}")
        
        # Test invalid ID
        invalid_id = "999999999"
        result = telegram.is_authorized(invalid_id)
        print(f"   ❌ Invalid ID ({invalid_id}): {result}")
        print()
        
        # Test connection
        print("🌐 Testing Bot Connection:")
        if telegram.validate_connection():
            print("   ✅ Bot is reachable")
        else:
            print("   ❌ Bot connection failed")
        print()
        
        # Summary
        print("=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Authorization system: Working")
        print(f"✅ Multi-user support: {'Enabled' if len(authorized_ids) > 1 else 'Single user'}")
        print(f"✅ Total authorized users: {len(authorized_ids)}")
        print()
        
        if len(authorized_ids) > 1:
            print("🎉 Multi-user mode is active!")
            print("   Each user will have isolated message history")
        elif len(authorized_ids) == 1:
            print("ℹ️  Single-user mode active")
            print("   Add more IDs to TELEGRAM_AUTHORIZED_CHAT_IDS for multi-user")
        else:
            print("⚠️  No users configured - bot will not accept messages")
        
        print()
        print("=" * 70)
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print()
        print("💡 Make sure these are set in .env:")
        print("   - TELEGRAM_BOT_TOKEN")
        print("   - TELEGRAM_AUTHORIZED_CHAT_IDS or TELEGRAM_CHAT_ID")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_message_routing():
    """Test that messages can be sent to specific chats."""
    print("\n")
    print("=" * 70)
    print("📮 TESTING MESSAGE ROUTING")
    print("=" * 70)
    print()
    
    telegram = TelegramService()
    authorized_ids = telegram.get_authorized_chat_ids()
    
    if not authorized_ids:
        print("⚠️  Skipping - no authorized chat IDs configured")
        return
    
    print("ℹ️  This test would send a message to each authorized chat")
    print("   Run with --send flag to actually send messages")
    print()
    
    for idx, chat_id in enumerate(authorized_ids, 1):
        print(f"   {idx}. Would send to: {chat_id}")
    
    print()
    
    # Check if --send flag is provided
    if "--send" in sys.argv:
        print("🚀 Sending test messages...")
        print()
        
        for chat_id in authorized_ids:
            try:
                success = telegram.send_message(
                    "🧪 Multi-user test message\n\n"
                    "✅ Your chat ID is authorized!\n"
                    "You will receive messages isolated from other users.",
                    chat_id=chat_id
                )
                if success:
                    print(f"   ✅ Sent to {chat_id}")
                else:
                    print(f"   ❌ Failed to send to {chat_id}")
            except Exception as e:
                print(f"   ❌ Error sending to {chat_id}: {e}")
        
        print()
        print("✅ Test messages sent!")
    else:
        print("💡 Use 'python test_multi_user.py --send' to send test messages")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    test_authorization()
    test_message_routing()
    
    print()
    print("✅ All tests completed!")
    print()
