# community/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q # للاستخدام في البحث
from django.core.paginator import Paginator # للتقسيم على صفحات
from django.http import HttpResponse # لاستخدام HTMX
import markdown2 # لتحويل Markdown إلى HTML
from django.contrib.contenttypes.models import ContentType # لاستخدام ContentType
from .models import Post, Comment, Like, Follow, Conversation, Message, Report
from .forms import PostForm, CommentForm, MessageForm, ReportForm
from users.models import CustomUser, Profile # للتأكد من استيراد CustomUser و Profile
from django.utils.translation import gettext_lazy as _ # للترجمة في الـ views


# دوال مساعدة لـ Markdown
def render_markdown_to_html(markdown_text):
    return markdown2.markdown(markdown_text, extras=["fenced-code-blocks", "tables", "footnotes"])

# دالة مساعدة للتحقق من هوية المشرف
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

# --------------------
# Community Post Views
# --------------------

@login_required
def post_list_view(request):
    """
    يعرض قائمة بجميع المنشورات في المجتمع، مع دعم البحث والتصفية.
    """
    query = request.GET.get('q')
    sort_by = request.GET.get('sort', '-created_at') # الترتيب الافتراضي: الأحدث
    
    posts = Post.objects.all().select_related('user').prefetch_related('likes_relation') # Preload user and likes
    
    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(user__username__icontains=query))
    
    posts = posts.order_by(sort_by)

    # تقسيم المنشورات على صفحات
    paginator = Paginator(posts, 10) # 10 منشورات لكل صفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # جلب المنشورات التي أعجب بها المستخدم الحالي
    liked_post_ids = Like.objects.filter(user=request.user, content_type__model='post').values_list('object_id', flat=True)

    # جلب ContentType IDs (هام لزر الإعجاب العام)
    post_content_type_id = ContentType.objects.get_for_model(Post).id
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'sort_by': sort_by,
        'liked_post_ids': set(liked_post_ids),
        'post_content_type_id': post_content_type_id, # تمرير ContentType ID للـ Post
        'create_post_form': PostForm() # لتوفير النموذج في الصفحة الرئيسية لإنشاء منشور جديد
    }
    return render(request, 'community/post_list.html', context)


@login_required
def post_detail_view(request, pk):
    """
    يعرض تفاصيل منشور واحد وجميع التعليقات عليه، مع نموذج لإضافة تعليق جديد.
    """
    post = get_object_or_404(Post.objects.select_related('user').prefetch_related('likes_relation'), pk=pk)
    
    # جلب التعليقات الرئيسية فقط، ومع كل تعليق، جلب الردود والإعجابات
    comments = Comment.objects.filter(post=post, parent__isnull=True).select_related('user').prefetch_related('replies__user', 'likes_relation', 'replies__likes_relation')
    
    comment_form = CommentForm()

    # جلب الإعجابات للمنشور وللتعليقات
    liked_post_ids = Like.objects.filter(user=request.user, content_type__model='post').values_list('object_id', flat=True)
    liked_comment_ids = Like.objects.filter(user=request.user, content_type__model='comment').values_list('object_id', flat=True)

    # جلب ContentType IDs (هام لزر الإعجاب العام)
    post_content_type_id = ContentType.objects.get_for_model(Post).id
    comment_content_type_id = ContentType.objects.get_for_model(Comment).id

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'liked_post_ids': set(liked_post_ids),
        'liked_comment_ids': set(liked_comment_ids),
        'post_content_type_id': post_content_type_id, # تمرير ContentType ID للـ Post
        'comment_content_type_id': comment_content_type_id, # تمرير ContentType ID للـ Comment
    }
    return render(request, 'community/post_detail.html', context)

@login_required
def post_create_view(request):
    """
    ينشئ منشورًا جديدًا.
    """
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, _('تم إنشاء المنشور بنجاح!'))
            return redirect('community:post_detail', pk=post.pk)
        else:
            messages.error(request, _('حدث خطأ أثناء إنشاء المنشور. الرجاء التحقق من البيانات.'))
    else:
        form = PostForm()
    return render(request, 'community/post_form.html', {'form': form, 'page_title': _('إنشاء منشور جديد')})

@login_required
def post_edit_view(request, pk):
    """
    يعدل منشورًا موجودًا.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.user:
        messages.error(request, _('ليس لديك صلاحية لتعديل هذا المنشور.'))
        return redirect('community:post_detail', pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث المنشور بنجاح!'))
            return redirect('community:post_detail', pk=post.pk)
        else:
            messages.error(request, _('حدث خطأ أثناء تحديث المنشور. الرجاء التحقق من البيانات.'))
    else:
        form = PostForm(instance=post)
    return render(request, 'community/post_form.html', {'form': form, 'page_title': _('تعديل المنشور')})

@login_required
def post_delete_view(request, pk):
    """
    يحذف منشورًا موجودًا.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.user and not request.user.is_superuser: # يمكن للمشرف الحذف أيضاً
        messages.error(request, _('ليس لديك صلاحية لحذف هذا المنشور.'))
        return redirect('community:post_detail', pk=pk)

    if request.method == 'POST':
        post.delete()
        messages.success(request, _('تم حذف المنشور بنجاح.'))
        return redirect('community:post_list')
    return render(request, 'community/post_confirm_delete.html', {'object': post, 'object_type': _('المنشور')})


# --------------------
# Comment Views
# --------------------

@login_required
def add_comment_to_post(request, pk):
    """
    يضيف تعليقًا جديدًا إلى منشور.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, _('تم إضافة تعليقك بنجاح!'))
            return redirect('community:post_detail', pk=post.pk)
        else:
            messages.error(request, _('حدث خطأ أثناء إضافة التعليق. الرجاء التحقق من البيانات.'))
    return redirect('community:post_detail', pk=post.pk) # إعادة توجيه إذا كان طلب GET


@login_required
def add_reply_to_comment(request, pk):
    """
    يضيف رداً على تعليق موجود.
    """
    parent_comment = get_object_or_404(Comment, pk=pk)
    post = parent_comment.post # المنشور الأصلي للتعليق
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.parent = parent_comment
            reply.user = request.user
            reply.save()
            messages.success(request, _('تم إضافة ردك بنجاح!'))
            return redirect('community:post_detail', pk=post.pk)
        else:
            messages.error(request, _('حدث خطأ أثناء إضافة الرد. الرجاء التحقق من البيانات.'))
    return redirect('community:post_detail', pk=post.pk) # إعادة توجيه إذا كان طلب GET


# --------------------
# Like/Follow Views
# --------------------

@login_required
def like_toggle_view(request, content_type_id, object_id):
    """
    يعالج الإعجاب/إلغاء الإعجاب بمنشور أو تعليق (عبر HTMX).
    """
    if request.method == 'POST':
        user = request.user
        try:
            content_type = ContentType.objects.get_for_id(content_type_id)
            obj = content_type.get_object_for_this_type(pk=object_id)
        except ContentType.DoesNotExist:
            return HttpResponse(status=404, content=_("نوع المحتوى غير موجود."))
        except Exception: # استخدام استثناء عام للتعامل مع أي خطأ في get_object_for_this_type
            return HttpResponse(status=404, content=_("العنصر غير موجود لهذا النوع من المحتوى."))

        liked = False
        try:
            like = Like.objects.get(user=user, content_type=content_type, object_id=object_id)
            like.delete() # إلغاء الإعجاب
        except Like.DoesNotExist:
            Like.objects.create(user=user, content_type=content_type, object_id=object_id) # إعجاب
            liked = True

        likes_count = obj.likes_relation.count() # استخدام likes_relation للحصول على العدد

        # تحديد ما إذا كان المستخدم الحالي قد أعجب بالعنصر
        user_has_liked = Like.objects.filter(user=user, content_type=content_type, object_id=object_id).exists()

        context = {
            'object_id': object_id,
            'likes_count': likes_count,
            'user_has_liked': user_has_liked,
            'content_type_id': content_type_id,
            'is_post': content_type.model == 'post',
            'is_comment': content_type.model == 'comment',
        }
        return render(request, 'community/partials/like_button.html', context)
    return HttpResponse(status=405, content=_("الوصول غير مسموح."))


@login_required
def follow_toggle_view(request, user_id):
    """
    يعالج متابعة/إلغاء متابعة المستخدمين (عبر HTMX).
    """
    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, pk=user_id)
        follower_user = request.user

        if follower_user == target_user:
            return HttpResponse(status=400, content=_("لا يمكنك متابعة نفسك."))

        followed = False
        try:
            follow = Follow.objects.get(follower=follower_user, followed=target_user)
            follow.delete() # إلغاء المتابعة
        except Follow.DoesNotExist:
            Follow.objects.create(follower=follower_user, followed=target_user) # متابعة
            followed = True
        
        followers_count = target_user.followers.count() # افتراضياً related_name 'followers'
        following_count = target_user.following.count() # افتراضياً related_name 'following'

        # تحديد ما إذا كان المستخدم الحالي يتابع المستخدم المستهدف
        user_is_following = Follow.objects.filter(follower=follower_user, followed=target_user).exists()

        context = {
            'target_user': target_user,
            'followers_count': followers_count,
            'following_count': following_count,
            'user_is_following': user_is_following,
        }
        return render(request, 'community/partials/follow_button.html', context)
    return HttpResponse(status=405, content=_("الوصول غير مسموح."))


# --------------------
# Private Messaging Views
# --------------------

@login_required
def inbox_view(request):
    """
    يعرض صندوق الوارد الخاص بالمستخدم (قائمة المحادثات).
    """
    # جلب جميع المحادثات التي يشارك فيها المستخدم
    conversations = request.user.conversations.all().prefetch_related('participants').order_by('-updated_at')
    
    # للتحقق من إذا كان المستخدم قد بدأ محادثة بالفعل مع شخص معين
    # ليس مطلوباً هنا بشكل مباشر، ولكن قد يكون مفيداً في المستقبل.

    context = {
        'conversations': conversations,
        'page_title': _('صندوق الرسائل')
    }
    return render(request, 'community/inbox.html', context)


@login_required
def start_new_conversation_view(request, user_id):
    """
    يبدأ محادثة جديدة مع مستخدم معين أو يعيد التوجيه إلى محادثة موجودة.
    """
    other_user = get_object_or_404(CustomUser, pk=user_id)
    current_user = request.user

    if current_user == other_user:
        messages.warning(request, _("لا يمكنك بدء محادثة مع نفسك."))
        return redirect('community:inbox') # أو أي صفحة مناسبة

    # البحث عن محادثة موجودة بين المستخدمين
    # يجب أن تكون هناك طريقة أكثر قوة للتحقق من المشاركين في ManyToManyField
    # الطريقة المباشرة تتطلب تكرارًا على المحادثات
    existing_conversation = None
    for convo in current_user.conversations.all():
        if other_user in convo.participants.all() and convo.participants.count() == 2:
            existing_conversation = convo
            break
    
    if existing_conversation:
        messages.info(request, _("لقد بدأت محادثة بالفعل مع هذا المستخدم."))
        return redirect('community:conversation_detail', pk=existing_conversation.pk)
    
    # إذا لم تكن هناك محادثة موجودة، قم بإنشاء واحدة جديدة
    conversation = Conversation.objects.create()
    conversation.participants.add(current_user, other_user)
    messages.success(request, _("تم بدء محادثة جديدة."))
    return redirect('community:conversation_detail', pk=conversation.pk)


@login_required
def conversation_detail_view(request, pk):
    """
    يعرض محتوى محادثة معينة.
    """
    conversation = get_object_or_404(Conversation, pk=pk)

    # التأكد من أن المستخدم الحالي هو مشارك في هذه المحادثة
    if request.user not in conversation.participants.all():
        messages.error(request, _("ليس لديك صلاحية لعرض هذه المحادثة."))
        return redirect('community:inbox')

    messages_in_convo = conversation.messages.all().select_related('sender')
    message_form = MessageForm()

    # وضع علامة 'مقروءة' على الرسائل المستلمة
    for msg in messages_in_convo.filter(is_read=False).exclude(sender=request.user):
        msg.is_read = True
        msg.save()

    context = {
        'conversation': conversation,
        'messages': messages_in_convo,
        'message_form': message_form,
        'page_title': _('محادثة')
    }
    return render(request, 'community/conversation.html', context)


@login_required
def send_message_view(request, pk):
    """
    يرسل رسالة جديدة داخل محادثة موجودة.
    """
    conversation = get_object_or_404(Conversation, pk=pk)

    if request.user not in conversation.participants.all():
        messages.error(request, _("ليس لديك صلاحية لإرسال رسائل في هذه المحادثة."))
        return redirect('community:inbox')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            # تحديث وقت آخر تحديث للمحادثة
            conversation.updated_at = timezone.now()
            conversation.save()
            messages.success(request, _("تم إرسال الرسالة بنجاح!"))
            # يمكن أن تكون هذه استجابة HTMX إذا أردت تحديث جزء من الصفحة فقط
            return redirect('community:conversation_detail', pk=conversation.pk)
        else:
            messages.error(request, _("حدث خطأ أثناء إرسال الرسالة. الرجاء التحقق من البيانات."))
    return redirect('community:conversation_detail', pk=conversation.pk)


# --------------------
# Reporting Views
# --------------------

@login_required
def report_content_view(request, content_type_id, object_id):
    """
    يعالج الإبلاغ عن منشور أو تعليق.
    """
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
    except ContentType.DoesNotExist:
        messages.error(request, _("نوع المحتوى غير موجود."))
        return redirect('community:post_list')
    except Exception:
        messages.error(request, _("العنصر المبلغ عنه غير موجود."))
        return redirect('community:post_list')
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.content_type = content_type
            report.object_id = object_id
            report.save()
            messages.success(request, _("تم إرسال البلاغ بنجاح. شكراً لك على مساعدتنا في الحفاظ على مجتمع آمن."))
            # إعادة التوجيه إلى صفحة تفاصيل العنصر المبلغ عنه أو قائمة المنشورات
            return redirect('community:post_detail', pk=obj.pk if hasattr(obj, 'pk') else obj.post.pk)
        else:
            messages.error(request, _("حدث خطأ أثناء إرسال البلاغ. الرجاء التحقق من البيانات."))
    else:
        form = ReportForm()

    context = {
        'form': form,
        'object': obj,
        'object_type_name': content_type.name, # اسم نوع المحتوى
        'page_title': _('الإبلاغ عن محتوى')
    }
    return render(request, 'community/report_form.html', context)

# --------------------
# Community Guidelines View
# --------------------

def guidelines_view(request):
    """
    يعرض صفحة إرشادات المجتمع.
    """
    return render(request, 'community/guidelines.html', {'page_title': _('إرشادات المجتمع')})

