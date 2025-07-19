# companion/views.py
import os
import google.generativeai as genai
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ChatMessage
from django.conf import settings # لاستيراد الإعدادات

# --- تهيئة Gemini API ---
# قم بتحميل مفتاح API من متغيرات البيئة (الذي تم إعداده في settings.py)
# هذا السطر يفترض أنك قمت بتحميل المتغيرات في settings.py
# إذا لم تفعل، يمكنك استخدام: from dotenv import load_dotenv; load_dotenv();
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(user_message, history):
    """
    منطق الروبوت (الإصدار الثالث مع Gemini API والذاكرة).
    """
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
        [f"المستخدم: {chat.message_text}\nرفيق الدرب: {chat.response_text}" for chat in history]
    )

    # 3. دمج التوجيهات مع سجل المحادثة والرسالة الجديدة
    full_prompt = system_prompt.format(chat_history=formatted_history)
    final_prompt = f"{full_prompt}\n\nالمستخدم: {user_message}\nرفيق الدرب:"
    
    try:
        # 4. إعداد النموذج واستدعاء الـ API
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(final_prompt)
        return response.text
    except Exception as e:
        # التعامل مع أي أخطاء من الـ API
        print(f"Error calling Gemini API: {e}")
        return "عذرًا، حدث خطأ أثناء محاولة الاتصال. الرجاء المحاولة مرة أخرى لاحقًا."


@login_required
def chatbot_view(request):
    # جلب آخر 10 رسائل فقط لإبقاء السياق مركزًا وتوفير التكلفة (Tokens)
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('timestamp')[:10]

    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        if user_message:
            # الحصول على رد الروبوت من Gemini
            bot_response = get_gemini_response(user_message, chat_history)

            # حفظ الرسالة والرد في قاعدة البيانات
            new_chat = ChatMessage.objects.create(
                user=request.user,
                message_text=user_message,
                response_text=bot_response
            )
            
            # (إذا كنت تستخدم HTMX)
            if 'HTTP_HX_REQUEST' in request.META:
                # تحديث السجل ليشمل الرسالة الجديدة للعرض الفوري
                updated_history = list(chat_history) + [new_chat]
                # لنرسل الرسالتين الأخيرتين (رسالة المستخدم ورد الروبوت)
                last_two_messages = updated_history[-2:] if len(updated_history) > 1 else [new_chat]
                
                # إنشاء قالب جزئي جديد لعرض رسالة المستخدم ورد الروبوت معًا
                return render(request, 'companion/partials/new_chat_entry.html', {'entry': new_chat})

    context = {
        'chat_history': chat_history
    }
    return render(request, 'companion/chatbot.html', context)