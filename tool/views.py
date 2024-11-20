from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import *
from django.shortcuts import render
import generateID
import generateNumber
import scrapper_
import otp_find


def signin(request):
    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']
        try:
            username = User.objects.get(username=username).username
        except Exception as e:
            messages.error(request, "Please check your Username")
            return render(request, 'pages/signin.html')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if 'admin' in username:
                return redirect('/adminDashboard')
            else:
                return redirect('/userDashboard')
        else:
            messages.error(request, "Please check your Password")
            return render(request, 'pages/signin.html')
    else:
        return render(request, 'pages/signin.html')


def adminDashboard(request):
    data_pass = {'data': email_info.objects.values().order_by('id'), 'total_ids': email_info.objects.values().count(),
                 'assigned': email_info.objects.filter(assigned=True).values().count(),
                 'remaining': email_info.objects.filter(assigned=False).values().count(),
                 'total_users': User.objects.values().count(), 'users_list': User.objects.values(),
                 'emails': email_info.objects.filter(assigned=False).values()}
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not username or not password:
            try:
                emails = request.POST.getlist('emails')
                user_id = int(request.POST.get('user_id'))
                user_instance = User.objects.get(id=user_id)
                en = assigned_emails(user=user_instance)
                en.save()
                en.emails.set(emails)
                for email in emails:
                    en = email_info.objects.filter(id=email)
                    en.update(assigned=True)
            except:
                pass
        else:
            user = User.objects.create_user(username=username, password=password)
        return redirect('/adminDashboard')
    return render(request, 'pages/adminDashboard.html', data_pass)


def userDashboard(request):
    user = request.user

    assigned_email_obj = assigned_emails.objects.filter(user=user).prefetch_related('emails')

    data = []
    for assigned_email in assigned_email_obj:

        email_details = assigned_email.emails.all()
        for email in email_details:
            data.append({
                "id":email.id,
                "email": email.email,
                "phone_number": email.phone_number,
                "order_id": email.order_id,
                "created_at": email.created_at,
                "assigned": email.assigned,
                "status": email.status,
            })
    data_pass = {'data': data}
    return render(request, 'pages/userDashboard.html', data_pass)


def generate_id(request):
    target = int(request.GET.get('target'))
    try:
        last_email_id = email_info.objects.values().order_by('-id')[0]['id']
    except Exception as e:
        last_email_id = 0
    list_ = []
    for i in range(target):
        response = generateID.func_(f'flipid{last_email_id + i + 1}')
        api_key = ("eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9"
                   ".eyJleHAiOjE3NTgwMTkwMjIsImlhdCI6MTcyNjQ4MzAyMiwicmF5IjoiOTllZTIzMDhmNjEzOTU1NzM1NzQ3NzIwZjEwZTJlMDMiLCJzdWIiOjE4NDY5OTF9.Zz1BslVsnHPfqw5BRoyJGVkI9AO_zd_t5hHeF5MWJGJBFGK2E7a06ZgplOGdQXms1uAFGJ_j5I-5AkEs_AoWE74CRjYX8UMhk-26Kxew9DKmIzCDKXobtsqOiEjWcAuB1-CPGFrlO8f1fJ7-ZT-9-zKEs2wMyM0ACOT7x5JJ2GKZiNWcbKFEJt1iHQdRS9JwF6JFH5S2xmYBrkDxgDc4JOCHHFf5SpONYaLRExy8sB9UThybpc3OnBb4c9AU50UPh9nD7ywaVyU5NxOHYBkIrrGKA01oTIJXSN0mgiTBT7xmGDtVoaevJjlEX9oOfAtVEiu4tUHCfnJtWqfoJjMm2w")
        result = generateNumber.create_5sim_phone(api_key)
        if result["status"] == "success":
            phone_number = result['phone']
            order_id = result['id']
        else:
            phone_number = None
            order_id = None
        if response:
            if email_info.objects.filter(email=f'flipid{last_email_id + i + 1}@idsbanao.com').values():
                pass
            else:
                en = email_info(email=f'flipid{last_email_id + i + 1}@idsbanao.com', phone_number=phone_number,
                                order_id=order_id)
                en.save()
                list_.append({'mobile_number': phone_number, 'email_id': f'flipid{last_email_id + i + 1}@idsbanao.com',
                              'order_id': order_id, 'id': en.id})
    return_list = scrapper_.func_main(len(list_), 0, len(list_), list_)
    for id_ in return_list:
        en = email_info.objects.filter(id=id_)
        en.update(status=True)
    data = {}
    return JsonResponse(data)


def delete(request, id):
    en = email_info.objects.filter(id=id)
    en.delete()
    return redirect('/adminDashboard')


def get_otp(request):
    id_ = request.GET.get('id_')
    email_id = email_info.objects.filter(id=id_).values()[0]['email']
    otp = otp_find.get_latest_otp(email_id)
    data={'otp':otp}
    return JsonResponse(data)
