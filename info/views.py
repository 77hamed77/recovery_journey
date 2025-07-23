# info/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.db.models import Count

from .models import Resource, ContactMessage
from .forms import ResourceForm, ContactMessageForm, AdminReplyForm

def is_superuser(user):
    """يتحقق مما إذا كان المستخدم أدمن (طبيب نفسي)."""
    return user.is_superuser

def about_view(request):
    """عرض صفحة 'من نحن'."""
    return render(request, 'info/about.html')

def privacy_view(request):
    """عرض صفحة 'سياسة الخصوصية وشروط الاستخدام'."""
    return render(request, 'info/privacy.html')

@login_required
def contact_view(request):
    """صفحة إرسال رسالة تواصل جديدة من المستخدم إلى الطبيب."""
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            cm = form.save(commit=False)
            cm.user = request.user
            cm.save()
            messages.success(request, 'تم إرسال رسالتك بنجاح، وسيرد عليك الطبيب قريبًا.')
            return redirect('info:contact_history')
    else:
        form = ContactMessageForm()
    return render(request, 'info/contact.html', {'form': form})

@login_required
def contact_history_view(request):
    """صفحة عرض سجل الرسائل المرسلة من المستخدم مع الردود إن وجدت."""
    msgs = ContactMessage.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'info/contact_history.html', {'messages': msgs})

@login_required
@user_passes_test(is_superuser)
def admin_dashboard(request):
    """
    لوحة تحكّم الطبيب النفسي مع مخططات وإحصائيات:
      - إجمالي الرسائل
      - رسائل بانتظار الرد
      - آخر 5 رسائل واردة
      - بيانات مخطط الرسائل الشهري ونسبة الردود
    """
    # إحصائيات أساسية
    total_messages   = ContactMessage.objects.count()
    pending_messages = ContactMessage.objects.filter(reply='', replied_at__isnull=True).count()
    replied_messages = total_messages - pending_messages
    recent_messages  = ContactMessage.objects.order_by('-created_at')[:5]

    # بيانات المخطط الشهري لآخر 6 أشهر
    now = timezone.now()
    start_date = (now.replace(day=1) - timezone.timedelta(days=180)).replace(day=1)
    stats_qs = ContactMessage.objects.filter(created_at__gte=start_date)
    stats = (
        stats_qs
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # تجهيز القوائم للفترات الستة
    labels = []
    counts = []
    month_cursor = start_date
    for _ in range(6):
        labels.append(month_cursor.strftime('%b %Y'))
        rec = next(
            (item for item in stats
             if item['month'].month == month_cursor.month and item['month'].year == month_cursor.year),
            None
        )
        counts.append(rec['count'] if rec else 0)
        month_cursor = (month_cursor + timezone.timedelta(days=32)).replace(day=1)

    context = {
        'total_messages': total_messages,
        'pending_messages': pending_messages,
        'replied_messages': replied_messages,
        'recent_messages': recent_messages,
        'chart_labels': labels,
        'chart_data': counts,
    }
    return render(request, 'info/admin/dashboard.html', context)

@login_required
@user_passes_test(is_superuser)
def admin_messages_list(request):
    """صفحة الأدمن لعرض جميع رسائل التواصل الواردة."""
    msgs = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'info/admin/messages_list.html', {'messages': msgs})

@login_required
@user_passes_test(is_superuser)
def admin_message_detail(request, pk):
    """صفحة الأدمن لعرض رسالة معينة والرد عليها."""
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        form = AdminReplyForm(request.POST, instance=msg)
        if form.is_valid():
            reply_obj = form.save(commit=False)
            reply_obj.replied_by = request.user
            reply_obj.replied_at = timezone.now()
            reply_obj.save()
            try:
                send_mail(
                    f'تم الرد على رسالتك: {msg.subject}',
                    f'طبيبك النفسي ردّ على رسالتك:\n\n{reply_obj.reply}',
                    settings.DEFAULT_FROM_EMAIL,
                    [msg.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, 'تم حفظ الرد وإخطار المستخدم عبر البريد.')
            return redirect('info:admin_messages_list')
    else:
        form = AdminReplyForm(instance=msg)

    return render(request, 'info/admin/message_detail.html', {
        'message_obj': msg,
        'form': form,
    })

def resources_list_view(request):
    """عرض جميع الموارد المتاحة."""
    resources = Resource.objects.all().order_by('-created_at')
    return render(request, 'info/resources.html', {'resources': resources})

def resource_detail_view(request, pk):
    """عرض تفاصيل مورد محدد."""
    resource = get_object_or_404(Resource, pk=pk)
    return render(request, 'info/resource_detail.html', {'resource': resource})

@login_required
@user_passes_test(is_superuser)
def resource_create_view(request):
    """صفحة إنشاء مورد جديد (للطبيب/الأدمن فقط)."""
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            res = form.save(commit=False)
            res.created_by = request.user
            res.save()
            messages.success(request, 'تم إنشاء المورد بنجاح!')
            return redirect('info:resources_list')
    else:
        form = ResourceForm()
    return render(request, 'info/resource_form.html', {
        'form': form,
        'page_title': 'إضافة مورد جديد',
        'submit_button_text': 'إضافة المورد',
    })

@login_required
@user_passes_test(is_superuser)
def resource_edit_view(request, pk):
    """صفحة تعديل مورد موجود (للطبيب/الأدمن فقط)."""
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المورد بنجاح!')
            return redirect('info:resource_detail', pk=resource.pk)
    else:
        form = ResourceForm(instance=resource)
    return render(request, 'info/resource_form.html', {
        'form': form,
        'resource': resource,
        'page_title': f'تعديل المورد: {resource.title}',
        'submit_button_text': 'تحديث المورد',
    })

@login_required
@user_passes_test(is_superuser)
def resource_confirm_delete_view(request, pk):
    """صفحة تأكيد حذف مورد (للطبيب/الأدمن فقط)."""
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'تم حذف المورد بنجاح!')
        return redirect('info:resources_list')
    return render(request, 'info/resource_confirm_delete.html', {'resource': resource})


def landing_view(request):
    """
    صفحة الهبوط للزائرين غير الموثّقين.
    إذا كان المستخدم مسجّل دخول، يُعاد توجيهه إلى لوحة التحكم.
    """
    if request.user.is_authenticated:
        return redirect('journal:dashboard')  # أو أي اسم URL للداشبورد
    return render(request, 'info/landing.html')