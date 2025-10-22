#!/usr/bin/env python3
"""
Test script for Dolphin OCR API endpoint.
"""

import requests
import json
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """Create a test image with text for OCR testing."""
    # Create a white image
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()
    
    # Add test text
    test_text = "Hello World!\nThis is a test document\nfor Dolphin OCR processing.\n\nTable:\n| Name | Age |\n|------|-----|\n| John | 25  |\n| Jane | 30  |"
    draw.text((50, 50), test_text, fill='black', font=font)
    
    return img

def test_dolphin_ocr(base_url="http://localhost:6060"):
    """Test the Dolphin OCR endpoint."""
    print("🧪 Testing Dolphin OCR API...")
    print(f"🌐 Server URL: {base_url}")
    
    # Create test image
    print("📸 Creating test image...")
    test_image = create_test_image()
    
    # Save to bytes
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Prepare the request
    files = {
        'file': ('test_image.png', img_bytes, 'image/png')
    }
    
    data = {
        'return_blocks': 'true',
        'language_hint': 'en'
    }
    
    try:
        print(f"🚀 Sending request to {base_url}/api/v1/ocr/dolphin...")
        response = requests.post(
            f"{base_url}/api/v1/ocr/dolphin",
            files=files,
            data=data,
            timeout=120  # Longer timeout for Dolphin processing
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Dolphin OCR request successful!")
            print(f"📝 Extracted text: {result['text']}")
            print(f"📄 Markdown output:")
            print("=" * 50)
            print(result['markdown'])
            print("=" * 50)
            print(f"⏱️  Processing time: {result['took_ms']}ms")
            print(f"🤖 Model: {result['model_id']}")
            print(f"📦 Number of blocks: {len(result['blocks'])}")
            
            if result['blocks']:
                print("\n📋 OCR Blocks:")
                for i, block in enumerate(result['blocks']):
                    print(f"  Block {i+1}: '{block['text']}' (type: {block.get('element_type', 'unknown')})")
            
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running.")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Dolphin processing might be taking too long.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_health_endpoint(base_url="http://localhost:6060"):
    """Test if the server is running."""
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Server is running!")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running.")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Dolphin OCR API Test Script")
    print("=" * 40)
    
    base_url = "http://localhost:6060"
    
    # Test server health first
    if not test_health_endpoint(base_url):
        print("\n💡 To start the server, run:")
        print("   docker-compose up -d")
        sys.exit(1)
    
    print()
    
    # Test Dolphin OCR endpoint
    success = test_dolphin_ocr(base_url)
    
    if success:
        print("\n🎉 All tests passed! Dolphin OCR is working correctly.")
    else:
        print("\n💥 Tests failed. Check the server logs for more details.")
        sys.exit(1)
