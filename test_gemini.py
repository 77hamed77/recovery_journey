#!/usr/bin/env python3
"""
ملف اختبار بسيط لمفتاح Gemini API
قم بتشغيله من مجلد المشروع الجذر
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# تحميل متغيرات البيئة
load_dotenv()

def test_gemini_api():
    # جلب مفتاح API
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # تكوين API
        genai.configure(api_key=api_key)
        
        # اختبار بسيط
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("مرحبا، كيف حالك؟")
        
        if response.text:
            print("✅ API Test Successful!")
            print(f"Response: {response.text}")
            return True
        else:
            print("❌ Empty response from API")
            return False
            
    except Exception as e:
        print(f"❌ API Test Failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Gemini API...")
    success = test_gemini_api()
    
    if success:
        print("\n🎉 API is working correctly!")
    else:
        print("\n⚠️ Please check your API key and try again.")