# community/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
import markdown2 # لمعالجة Markdown
import re # للكشف عن @Mentions

from users.models import CustomUser, Profile # لاستخدام Profile
from .models import Post, Comment, Like, Follow, Conversation, Message, Report
from .forms import PostForm, CommentForm, MessageForm, ReportForm

# دالة مساعدة لمعالجة المحتوى (Markdown و Mentions)
def process_content(content):
    # تحويل Markdown إلى HTML
    html_content = markdown2.markdown(content, extras=["fenced-code-blocks", "tables", "strike", "code-friendly"])
    
    # تحويل @mentions إلى روابط للملفات الشخصية (مثال بسيط)
    # هذا يتطلب وجود مسار URL لملف شخصي للمستخدم
    # حالياً لا يوجد مسار لملف شخصي، لذا سنقوم فقط بتمييز الاسم
    # إذا أردت مساراً حقيقياً، ستحتاج إلى:
    # 1. إضافة مسار 'users/<username>/' في users/urls.py
    # 2. إضافة دالة عرض (view) تعرض ملف المستخدم الشخصي.
    # 3. استبدال "#" بـ reverse('users:profile_detail', kwargs={'username': match.group(1)})
    
    # regex = r'@(\w+)' # يبحث عن @ ثم أي كلمة (حروف وأرقام وشرطات سفلية)
    # def replace_mention(match):
    #     username = match.group(1)
    #     try:
    #         user = CustomUser.objects.get(username=username)
    #         # في هذه الحالة، سنضيف رابطًا وهميًا أو نكتفي بتمييز الاسم
    #         return f'<a href="/users/{user.username}/" class="text-primary-dark font-semibold hover:underline">@{username}</a>'
    #     except CustomUser.DoesNotExist:
    #         return match.group(0) # إذا لم يتم العثور على المستخدم، نترك النص كما هو
    # html_content = re.sub(regex, replace_mention, html_content)
    
    # حالياً، نكتفي بتمييز المستخدمين بدون ربط بمسار URL (حتى يتم إنشاء مسار ملف شخصي)
    html_content = re.sub(r'@(\w+)', r'<span class="text-primary-dark font-semibold">@\1</span>', html_content)

    return html_content


@login_required
def post_list_view(request):
    """
    يعرض قائمة بجميع منشورات المجتمع.
    """
    posts = Post.objects.all()
    
    # جلب حالة الإعجاب للمستخدم الحالي
    liked_posts = Like.objects.filter(user=request.user, content_type=ContentType.objects.get_for_model(Post)).values_list('object_id', flat=True)
    
    context = {
        'posts': posts,
        'liked_posts': set(liked_posts), # تحويلها إلى مجموعة لسرعة البحث
    }
    return render(request, 'community/post_list.html', context)

@login_required
def post_detail_view(request, post_id):
    """
    يعرض تفاصيل منشور واحد، ويسمح للمستخدمين بإضافة تعليقات وردود.
    """
    post = get_object_or_404(Post, id=post_id)
    
    # جلب التعليقات الرئيسية (بدون أب) وفرزها
    # ثم جلب الردود لكل تعليق رئيسي
    top_level_comments = Comment.objects.filter(post=post, parent__isnull=True).order_by('created_at')
    
    # جلب حالة الإعجاب للمستخدم الحالي للمنشور والتعليقات
    liked_post = Like.objects.filter(user=request.user, content_type=ContentType.objects.get_for_model(Post), object_id=post.id).exists()
    
    liked_comments_ids = Like.objects.filter(user=request.user, content_type=ContentType.objects.get_for_model(Comment)).values_list('object_id', flat=True)

    if request.method == 'POST':
        # تحديد ما إذا كان التعليق رداً (إذا كان هناك comment_id في POST)
        parent_comment_id = request.POST.get('parent_comment_id')
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            if parent_comment_id:
                new_comment.parent = get_object_or_404(Comment, id=parent_comment_id, post=post)
            new_comment.save()
            messages.success(request, "تم إضافة تعليقك/ردك بنجاح!")
            return redirect('community:post_detail', post_id=post.id)
        else:
            messages.error(request, "حدث خطأ أثناء إضافة التعليق/الرد. الرجاء مراجعة البيانات.")
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'top_level_comments': top_level_comments,
        'comment_form': form,
        'liked_post': liked_post,
        'liked_comments_ids': set(liked_comments_ids),
        'process_content': process_content, # تمرير الدالة لمعالجة المحتوى في القالب
    }
    return render(request, 'community/post_detail.html', context)

@login_required
def post_create_view(request):
    """
    يسمح للمستخدمين بإنشاء منشور جديد.
    """
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "تم إنشاء منشورك بنجاح!")
            return redirect('community:post_list')
        else:
            messages.error(request, "حدث خطأ أثناء إنشاء المنشور. الرجاء التحقق من البيانات.")
    else:
        form = PostForm()
    
    context = {
        'form': form,
        'is_create': True,
    }
    return render(request, 'community/post_form.html', context)

@login_required
def post_edit_view(request, post_id):
    """
    يسمح للمستخدمين بتعديل منشوراتهم الخاصة.
    """
    post = get_object_or_404(Post, id=post_id)
    
    if post.user != request.user:
        messages.error(request, "لا تملك الإذن لتعديل هذا المنشور.")
        return redirect('community:post_detail', post_id=post.id)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث المنشور بنجاح!")
            return redirect('community:post_detail', post_id=post.id)
        else:
            messages.error(request, "حدث خطأ أثناء تحديث المنشور. الرجاء التحقق من البيانات.")
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'is_create': False,
    }
    return render(request, 'community/post_form.html', context)

@login_required
def post_delete_view(request, post_id):
    """
    يسمح للمستخدمين بحذف منشوراتهم الخاصة.
    """
    post = get_object_or_404(Post, id=post_id)
    
    if post.user != request.user:
        messages.error(request, "لا تملك الإذن لحذف هذا المنشور.")
        return redirect('community:post_detail', post_id=post.id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, "تم حذف المنشور بنجاح!")
        return redirect('community:post_list')
    
    context = {
        'post': post,
    }
    return render(request, 'community/post_confirm_delete.html', context)

@login_required
def like_content_view(request, content_type_id, object_id):
    """
    معالجة الإعجاب/إلغاء الإعجاب بمنشور أو تعليق.
    """
    if request.method == 'POST':
        content_type = get_object_or_404(ContentType, id=content_type_id)
        
        # جلب الكائن المستهدف (منشور أو تعليق)
        model_class = content_type.model_class()
        obj = get_object_or_404(model_class, id=object_id)

        try:
            with transaction.atomic():
                like, created = Like.objects.get_or_create(user=request.user, content_type=content_type, object_id=object_id)
                if not created: # إذا كان الإعجاب موجوداً بالفعل، قم بحذفه (إلغاء الإعجاب)
                    like.delete()
                    is_liked = False
                    messages.info(request, "تم إلغاء الإعجاب.")
                else:
                    is_liked = True
                    messages.success(request, "أعجبت بالمحتوى!")
            
            # إرجاع رد JSON أو HTML جزئي (إذا كنت تستخدم HTMX)
            # لحساب الإعجابات في الوقت الفعلي
            likes_count = model_class.objects.get(id=object_id).get_likes_count
            return JsonResponse({'is_liked': is_liked, 'likes_count': likes_count})

        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء معالجة الإعجاب: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    return HttpResponseBadRequest("Invalid request method.")


@login_required
def follow_user_view(request, user_id):
    """
    معالجة متابعة/إلغاء متابعة المستخدمين.
    """
    if request.method == 'POST':
        user_to_follow = get_object_or_404(CustomUser, id=user_id)

        if request.user == user_to_follow:
            return JsonResponse({'error': 'لا يمكنك متابعة نفسك.'}, status=400)
        
        try:
            with transaction.atomic():
                follow, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
                if not created:
                    follow.delete()
                    is_following = False
                    messages.info(request, f"تم إلغاء متابعة {user_to_follow.username}.")
                else:
                    is_following = True
                    messages.success(request, f"أنت الآن تتابع {user_to_follow.username}!")
            
            followers_count = Follow.objects.filter(followed=user_to_follow).count()
            following_count = Follow.objects.filter(follower=user_to_follow).count() # للتوضيح، قد لا تعرض هذه في الـ JSON

            return JsonResponse({
                'is_following': is_following,
                'followers_count': followers_count,
            })
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء معالجة المتابعة: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    return HttpResponseBadRequest("Invalid request method.")

@login_required
def report_content_view(request, content_type_id, object_id):
    """
    معالجة بلاغات المحتوى (منشور أو تعليق).
    """
    content_type = get_object_or_404(ContentType, id=content_type_id)
    model_class = content_type.model_class()
    obj = get_object_or_404(model_class, id=object_id)

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.content_type = content_type
            report.object_id = object_id
            report.save()
            messages.success(request, "تم إرسال بلاغك بنجاح. شكراً لك!")
            return redirect(obj.get_absolute_url()) # العودة إلى صفحة المحتوى المبلغ عنه
        else:
            messages.error(request, "حدث خطأ أثناء إرسال البلاغ. الرجاء مراجعة البيانات.")
    else:
        form = ReportForm()

    context = {
        'form': form,
        'content_object': obj,
        'content_type_id': content_type_id,
        'object_id': object_id,
    }
    return render(request, 'community/report_form.html', context)


@login_required
def inbox_view(request):
    """
    يعرض صندوق الوارد الخاص بالمستخدم (قائمة المحادثات).
    """
    conversations = request.user.conversations.all().order_by('-updated_at')
    context = {
        'conversations': conversations
    }
    return render(request, 'community/inbox.html', context)


@login_required
def conversation_detail_view(request, conversation_id):
    """
    يعرض تفاصيل محادثة معينة ورسائلها، ويسمح بإرسال رسائل جديدة.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # التأكد من أن المستخدم الحالي هو أحد المشاركين في المحادثة
    if request.user not in conversation.participants.all():
        messages.error(request, "لا تملك الإذن لعرض هذه المحادثة.")
        return redirect('community:inbox')

    messages_in_conversation = conversation.messages.all()
    
    # وضع علامة "مقروءة" على الرسائل غير المقروءة للمستخدم الحالي
    for message in messages_in_conversation.filter(is_read=False).exclude(sender=request.user):
        message.is_read = True
        message.save()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.conversation = conversation
            new_message.sender = request.user
            new_message.save()
            # تحديث وقت آخر تحديث للمحادثة
            conversation.updated_at = timezone.now()
            conversation.save()
            messages.success(request, "تم إرسال رسالتك!")
            return redirect('community:conversation_detail', conversation_id=conversation.id)
        else:
            messages.error(request, "حدث خطأ أثناء إرسال الرسالة.")
    else:
        form = MessageForm()

    context = {
        'conversation': conversation,
        'messages': messages_in_conversation,
        'message_form': form
    }
    return render(request, 'community/conversation.html', context)


@login_required
def start_new_conversation_view(request, user_id):
    """
    يبدأ محادثة جديدة مع مستخدم معين، أو يعيد توجيه إلى محادثة موجودة.
    """
    recipient = get_object_or_404(CustomUser, id=user_id)

    if request.user == recipient:
        messages.error(request, "لا يمكنك بدء محادثة خاصة مع نفسك.")
        return redirect('community:inbox') # أو صفحة الملف الشخصي للمستخدم

    # البحث عن محادثة موجودة بين المستخدمين (بغض النظر عن الترتيب)
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=recipient).first()

    if not conversation:
        # إذا لم تكن هناك محادثة، قم بإنشاء واحدة
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, recipient)
        conversation.save()
        messages.info(request, f"تم بدء محادثة جديدة مع {recipient.username}.")
    else:
        messages.info(request, f"أنت بالفعل تجري محادثة مع {recipient.username}.")

    return redirect('community:conversation_detail', conversation_id=conversation.id)


def community_guidelines_view(request):
    """
    يعرض صفحة إرشادات المجتمع.
    """
    return render(request, 'community/guidelines.html')

