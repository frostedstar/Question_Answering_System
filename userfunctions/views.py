from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import HttpResponse
from django.db.models import Q
from .models import Userinfo
from .models import ReadUserInfo
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from sendEmail.views import emailForVerification
from django.contrib.auth.hashers import make_password, check_password
from time import sleep
from django.conf import settings

user_list = []


# 老师的邮箱

def test(request):
    return render(request, 'test.html')


# 获取登录信息
def getUserInfo(request):
    return {
        'id': request.session.get('id'),
        'userId': request.session.get('userId'),
        'userName': request.session.get('userName'),
        'studentId': request.session.get('studentId'),
        # 'password': request.session.get('password'),
        'email': request.session.get('email'),
        'type': request.session.get('type'),
    }


# 上传登录信息
def setUserInfo(request, userInfo):
    request.session['id'] = userInfo.id
    request.session['userId'] = userInfo.user_id
    request.session['userName'] = userInfo.user_name
    request.session['studentId'] = userInfo.student_id
    request.session['password'] = userInfo.password
    request.session['email'] = userInfo.email
    request.session['type'] = userInfo.type
    request.session['approved'] = userInfo.approved


def login(request):
    request.session.flush()
    messages.error(request, "")

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = ReadUserInfo.objects.filter(user_name=username)
        if user.exists():
            userInfo = user.first()
            if check_password(password, userInfo.password):
                setUserInfo(request, userInfo)
                if not userInfo.approved:
                    messages.error(request, "该账户注册尚未通过")
                    return render(request, 'login.html')

                if (userInfo.type == "manager"):
                    return redirect('userManagement')
                else:
                    return redirect('index')
            else:
                messages.error(request, "用户名或密码错误")
        else:
            messages.error(request, "用户名或密码错误")
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        studentId = request.POST.get('studentId', '')
        password = request.POST.get('password', '')
        confirmPassword = request.POST.get('confirmPassword', '')
        email = request.POST.get('email', '')

        errors = {}
        # 校验逻辑
        if ReadUserInfo.objects.filter(user_name=username).exists():
            errors['username'] = '用户名已存在'
        if ReadUserInfo.objects.filter(student_id=studentId).exists():
            errors['studentId'] = '学号已注册'
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,20}$', password):
            errors['password'] = '要求包含数字、大写字母和小写字母,长度8~20位'
        if password != confirmPassword:
            errors['confirm_password'] = '两次输入密码不一致'
        if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', email):
            errors['email'] = '请输入有效的邮箱地址'

        if errors:
            # 返回 JSON 错误
            return JsonResponse({"success": False, "errors": errors})

        # 先返回等待提示
        emailContent = f"收到注册申请，用户信息如下:\n用户名:{username}\n学生id:{studentId}"
        teacherEmail = settings.TEACHER_EMAIL
        result = emailForVerification("注册申请", emailContent, teacherEmail)

        if result == "发送成功":  # 邮件发送成功
            # 保存用户
            Userinfo.objects.create(
                user_name=username,
                password=make_password(password),
                student_id=studentId,
                type="student",
                email=email,
                approved=0
            )
            return JsonResponse({
                "success": True,
                "message": "注册申请提交成功！即将跳转登录页面...",
                "redirect_url": "/login/"
            })
        else:
            return JsonResponse({
                "success": False,
                "errors": {"email": "邮件发送失败，请稍后重试"}
            })

    return render(request, 'register.html')


def userManagement(request):
    userInfo = getUserInfo(request)
    if userInfo["userId"] is None:
        return redirect('login')

    page_number = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 5))

    total_users = ReadUserInfo.objects.filter(~Q(user_id=userInfo["userId"]), approved=1).count()
    total_pages = (total_users + per_page - 1) // per_page

    start_index = (page_number - 1) * per_page
    end_index = start_index + per_page
    page_users = ReadUserInfo.objects.filter(~Q(user_id=userInfo["userId"]), approved=1).order_by('id')[
                 start_index:end_index]

    per_page_options = [5, 10, 20, 50]
    context = {
        'page_users': page_users,
        'page_number': page_number,
        'total_pages': total_pages,
        'per_page': per_page,
        'per_page_options': per_page_options,
    }
    return render(request, 'userManagement.html', context)


# 重置密码
@require_POST
def reset_password(request, user_id):
    user = ReadUserInfo.objects.filter(user_id=user_id).first()
    # user = get_object_or_404(ReadUserInfo, user_id=userId)
    user.password = make_password('123456')  # 示例：重置为默认密码
    user.save(update_fields=['password'])
    return redirect(request.META.get('HTTP_REFERER', '/'))


# 修改权限
@require_POST
def change_permission(request, user_id):
    user = ReadUserInfo.objects.filter(user_id=user_id).first()
    user.type = request.POST.get('permission')
    user.save(update_fields=['type'])
    return redirect(request.META.get('HTTP_REFERER', '/'))


# 删除用户
@require_POST
def delete_user(request, user_id):
    user = ReadUserInfo.objects.filter(user_id=user_id).first()
    user.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


def questionAnswerViews(request):
    return render(request, 'questionAnswerViews.html')


def profile(request):
    user_info = getUserInfo(request)
    if user_info["id"] is None:
        return redirect('login')

    return render(request, 'profile.html', {'user_info': user_info})


# 更新个人信息
@csrf_exempt
def update_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            field = data.get('field')
            value = data.get('value')
            userInfo = getUserInfo(request)

            # id = request.session.get('id')

            if userInfo["userId"] is None:
                return JsonResponse({'success': False, 'error': '用户未登录'})

            user = ReadUserInfo.objects.get(user_id=userInfo["userId"])

            # 验证字段
            if field not in ['username', 'email']:
                return JsonResponse({'success': False, 'error': '字段非法'})

            if field == 'username':
                user.user_name = value
                user.save(update_fields=['user_name'])
                request.session['userName'] = value


            elif field == 'email':
                if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', value):
                    return JsonResponse({'success': False, 'error': '请输入正确的邮箱地址'})
                user.email = value
                user.save(update_fields=['email'])
                request.session['email'] = value

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


# 修改密码
@csrf_exempt
def update_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            currentPassword = data.get('current_password')
            newPassword = data.get('new_password')
            confirmPassword = data.get('confirm_password')
            userInfo = getUserInfo(request)

            userId = request.session.get('userId')

            if userInfo["userId"] is None:
                return JsonResponse({'success': False, 'error': '用户未登录'})

            user = ReadUserInfo.objects.get(user_id=userInfo["userId"])

            if (not currentPassword) or (not newPassword) or (not confirmPassword):
                return JsonResponse({'success': False, 'error': '请输入内容'})
            if not check_password(currentPassword, user.password):
                return JsonResponse({'success': False, 'error': '原密码错误'})
            if currentPassword == newPassword:
                return JsonResponse({'success': False, 'error': '密码重复'})
            if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,20}$', newPassword):
                return JsonResponse({'success': False, 'error': '密码要求包含数字、大写字母和小写字母,长度8~20位'})
            if newPassword != confirmPassword:
                return JsonResponse({'success': False, 'error': '两次输入的密码不一致'})

            userInfo["userId"]
            user.password = make_password(newPassword)
            user.save(update_fields=['password'])
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


def registrationManagement(request):
    userInfo = getUserInfo(request)
    if userInfo["userId"] is None:
        return redirect('login')

    page_number = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 5))

    total_users = ReadUserInfo.objects.filter(approved=0).count()
    total_pages = (total_users + per_page - 1) // per_page

    start_index = (page_number - 1) * per_page
    end_index = start_index + per_page
    page_users = ReadUserInfo.objects.filter(approved=0).order_by('id')[start_index:end_index]

    per_page_options = [5, 10, 20, 50]
    context = {
        'page_users': page_users,
        'page_number': page_number,
        'total_pages': total_pages,
        'per_page': per_page,
        'per_page_options': per_page_options,
    }
    return render(request, 'registrationManagement.html', context)


# 注册通过
@require_POST
def registrationApprove(request, user_id):
    user = ReadUserInfo.objects.filter(user_id=user_id).first()
    # user = get_object_or_404(Userinfo, pk=user_id)
    user.approved = '1'
    user.save(update_fields=['approved'])
    userName = user.user_name
    emailContent = f"{userName},您的注册申请已通过"
    userEmail = [user.email]
    result = emailForVerification("注册申请通过", emailContent, userEmail)
    redirect_url = request.META.get('HTTP_REFERER', '/')

    if result == "发送成功":  # 假设 result=True 表示邮件发送成功

        return JsonResponse({
            "success": True,
            "message": "邮件发送成功",
            "redirect_url": redirect_url
        })
    else:
        return JsonResponse({
            "success": False,
            "errors": "邮件发送失败，请稍后重试"
        })


# 注册拒绝
@require_POST
def registrationDeny(request, user_id):
    user = ReadUserInfo.objects.filter(user_id=user_id).first()
    user.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))

