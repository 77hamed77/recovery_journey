# community/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment
from .forms import PostForm, CommentForm

@login_required
def post_list_view(request):
    """
    يعرض قائمة بجميع منشورات المجتمع.
    """
    posts = Post.objects.all()
    context = {
        'posts': posts,
    }
    return render(request, 'community/post_list.html', context)

@login_required
def post_detail_view(request, post_id):
    """
    يعرض تفاصيل منشور واحد، ويسمح للمستخدمين بإضافة تعليقات.
    """
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all() # جلب جميع التعليقات المرتبطة بالمنشور

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            messages.success(request, "تم إضافة تعليقك بنجاح!")
            return redirect('community:post_detail', post_id=post.id)
        else:
            messages.error(request, "حدث خطأ أثناء إضافة التعليق. الرجاء مراجعة البيانات.")
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
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
        'is_create': True, # لإعلام القالب بأن هذا نموذج إنشاء
    }
    return render(request, 'community/post_form.html', context)

@login_required
def post_edit_view(request, post_id):
    """
    يسمح للمستخدمين بتعديل منشوراتهم الخاصة.
    """
    post = get_object_or_404(Post, id=post_id)
    
    # التأكد من أن المستخدم الحالي هو صاحب المنشور
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
        'is_create': False, # لإعلام القالب بأن هذا نموذج تعديل
    }
    return render(request, 'community/post_form.html', context)

@login_required
def post_delete_view(request, post_id):
    """
    يسمح للمستخدمين بحذف منشوراتهم الخاصة.
    """
    post = get_object_or_404(Post, id=post_id)
    
    # التأكد من أن المستخدم الحالي هو صاحب المنشور
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

