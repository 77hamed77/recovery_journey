# companion/views.py
import os
import google.generativeai as genai
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ChatMessage
from django.conf import settings
import logging

# إعداد نظام السجلات للتشخيص
logger = logging.getLogger(__name__)

# --- تهيئة Gemini API ---
# طباعة حالة مفتاح API للتشخيص (احذف هذا بعد الإصلاح)
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    print(f"API Key loaded: {api_key[:10]}...{api_key[-4:]}")  # عرض جزء من المفتاح للتأكد
    genai.configure(api_key=api_key)
else:
    print("ERROR: GOOGLE_API_KEY not found in environment variables!")

def get_gemini_response(user_message, history):
    """
    منطق الروبوت مع تشخيص أفضل للأخطاء
    """
    # التحقق من وجود مفتاح API
    if not api_key:
        logger.error("GOOGLE_API_KEY not configured")
        return "خطأ: لم يتم تكوين مفتاح API. تأكد من إعداد GOOGLE_API_KEY في متغيرات البيئة."
    
    # 1. صياغة شخصية وتوجيهات الروبوت (System Prompt)
    system_prompt = """
    أنت "رفيق الدرب"، مساعد ذكاء اصطناعي داعم ومتعاطف. مهمتك هي مساعدة المستخدم في رحلة التعافي من الإدمان.
    قواعدك هي:
    1. كن دائمًا إيجابيًا، ومشجعًا، وغير قضائي (لا تصدر أحكامًا).
    2. استمع بعناية إلى مشاعر المستخدم وأفكاره.
    3. لا تقدم أبدًا نصائح طبية أو علاجية مباشرة. بدلاً من ذلك، شجع على التفكير الذاتي واقتراح آليات تأقلم صحية (مثل التأمل، المشي، الكتابة).
    4. إذا عبر المستخدم عن أفكار لإيذاء النفس أو خطر شديد، يجب أن ترد فورًا برسالة تحثه على طلب المساعدة المتخصصة وتوفير رقم خط المساعدة النفسية (إذا كان متاحًا بشكل عام).
    5. حافظ على الردود قصيرة نسبيًا ومركزة.
    6. استخدم سجل المحادثة السابق لفهم السياق وتقديم دعم أكثر تخصيصًا.
    
    هذا هو سجل المحادثة حتى الآن. استخدمه لفهم السياق:
    {chat_history}
    """

    # 2. تنسيق سجل المحادثات ليكون مفهومًا لـ Gemini
    formatted_history = "\n".join(
        [f"المستخدم: {chat.message}\nرفيق الدرب: {chat.response}" for chat in history]
    )

    # 3. دمج التوجيهات مع سجل المحادثة والرسالة الجديدة
    full_prompt = system_prompt.format(chat_history=formatted_history)
    final_prompt = f"{full_prompt}\n\nالمستخدم: {user_message}\nرفيق الدرب:"
    
    try:
        # 4. إعداد النموذج واستدعاء الـ API
        print(f"Attempting to call Gemini API for message: {user_message}")
        
        # تجربة نموذج مختلف إذا كان gemini-pro لا يعمل
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(final_prompt)
            
            # التحقق من وجود محتوى في الرد
            if response.text:
                print("Gemini API call successful")
                return response.text
            else:
                logger.error("Empty response from Gemini API")
                return "عذراً، تم الحصول على رد فارغ من الخدمة."
                
        except Exception as model_error:
            # محاولة استخدام نموذج آخر
            logger.error(f"Error with gemini-pro model: {model_error}")
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(final_prompt)
                if response.text:
                    return response.text
                else:
                    return "عذراً، تم الحصول على رد فارغ من الخدمة."
            except Exception as flash_error:
                logger.error(f"Error with gemini-1.5-flash model: {flash_error}")
                raise model_error  # إرجاع الخطأ الأصلي
        
    except Exception as e:
        # طباعة تفاصيل الخطأ للتشخيص
        error_msg = str(e)
        logger.error(f"Detailed error calling Gemini API: {error_msg}")
        print(f"Gemini API Error Details: {error_msg}")
        
        # رسائل خطأ مخصصة حسب نوع الخطأ
        if "API_KEY_INVALID" in error_msg:
            return "خطأ: مفتاح API غير صحيح. يرجى التحقق من مفتاح Gemini API."
        elif "PERMISSION_DENIED" in error_msg:
            return "خطأ: مفتاح API لا يملك الصلاحيات المطلوبة."
        elif "QUOTA_EXCEEDED" in error_msg:
            return "خطأ: تم تجاوز حد الاستخدام المسموح لـ API."
        else:
            return f"عذراً، حدث خطأ أثناء محاولة الاتصال: {error_msg}"


@login_required
def chatbot_view(request):
    # جلب آخر 10 رسائل فقط لإبقاء السياق مركزًا وتوفير التكلفة (Tokens)
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('timestamp')[:10]

    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        if user_message:
            print(f"Processing message: {user_message}")
            
            # الحصول على رد الروبوت من Gemini
            bot_response = get_gemini_response(user_message, chat_history)
            
            print(f"Bot response: {bot_response}")

            # حفظ الرسالة والرد في قاعدة البيانات
            new_chat = ChatMessage.objects.create(
                user=request.user,
                message=user_message,
                response=bot_response
            )
            
            # (إذا كنت تستخدم HTMX)
            if 'HTTP_HX_REQUEST' in request.META:
                return render(request, 'companion/partials/new_chat_entry.html', {'entry': new_chat})

    context = {
        'chat_history': chat_history
    }
    return render(request, 'companion/chatbot.html', context)