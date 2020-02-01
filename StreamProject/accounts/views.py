from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm, EmailPasswordForm
from .models import Profile, Contact
from common.decorators import ajax_required
from taggit.models import Tag
from images.models import Stream
import json
from requests import Session

@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user,
                                              user_to=user)
            else:
                Contact.objects.filter(user_from=request.user,
                                       user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'ko'})
    return JsonResponse({'status': 'ko'})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True).exclude(id=request.user.id)
    return render(request, 'accounts/user/list.html', {'section': 'people', 'users': users})


@login_required
def user_followers(request):
    usr = request.user
    users = usr.followers.all
    return render(request, 'accounts/user/list.html', {'section': 'people','users': users})


@login_required
def user_following(request):
    usr = request.user
    users = usr.following.all
    return render(request, 'accounts/user/list.html', {'section': 'people','users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'accounts/user/detail.html', {'section': 'people', 'user': user})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)

        if user_form.is_valid():
            if User.objects.filter(email=user_form.cleaned_data['email']):
                # return HttpResponse('User Already Exist')
                messages.error(request, 'User Already Exists')
            else:
                new_user = user_form.save(commit=False)
                new_user.set_password(user_form.cleaned_data['password'])
                new_user.save()
                profile = Profile.objects.create(user=new_user)
                return render(request,
                              'accounts/register_done.html',
                              {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'user_form': user_form})


@login_required
def dashboard(request, tag_slug=None):
    usrs = User.objects.filter(rel_to_set__user_from=request.user)
    streams = Stream.objects.filter(user__in=usrs).order_by('-created')
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        streams = streams.filter(tags__in=[tag])
    page = request.GET.get('page', 1)
    paginator = Paginator(streams, 4)
    try:
        streams = paginator.page(page)
    except PageNotAnInteger:
        streams = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        boostreamsks = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'streams/list_ajax.html',
                      {'section': 'streams', 'streams': streams})
    return render(request,
                  'accounts/dashboard.html',
                  {'section': 'dashboard', 'streams': streams})


@login_required
def user_streams(request, tag_slug=None):
    streams = Stream.objects.all()
    all_res = []
    for stream in streams:
        username = getattr(stream, 'user_name')
        clientId= "yx253jsyhtua7kycwmhpnxja32qqm8"
        apiRequestUrl = 'https://api.twitch.tv/kraken/users?login='+username
        session = Session()
        response = session.get(apiRequestUrl, headers={
        'Client-ID': clientId,
        'Accept': 'application/vnd.twitchtv.v5+json',
        'Content-Type': 'application/json'
        })
        session = Session()
        stream = json.loads(response.text)
        user_id = stream['users'][0]['_id']
        apiRequestUrl = 'https://api.twitch.tv/kraken/channels/'+user_id
        response = session.get(apiRequestUrl, headers={
        'Client-ID': clientId,
        'Accept': 'application/vnd.twitchtv.v5+json',
        'Content-Type': 'application/json'
        })
        stream = json.loads(response.text)
        banner = stream['video_banner']
        if banner is None:
            banner = "C:/Users/ajava/Desktop/streaming.png"
        current_res = {
            'user_name' : username,
            'url' : 'http://127.0.0.1:8000/my_stream_details/' + username,
            'banner' : banner
        }
        all_res.append(current_res)
    page = request.GET.get('page', 1)
    paginator = Paginator(all_res, 3)
    try:
        all_res = paginator.page(page)
    except PageNotAnInteger:
        all_res = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        all_res = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'streams/my_stream_list_ajax.html',
                      {'section': 'streams', 'streams': all_res})
    return render(request,
                  'accounts/user_streams.html',
                  {'section': 'people', 'streams': all_res})


@login_required()
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'accounts/edit.html', {'user_form': user_form, 'profile_form': profile_form})


def reset_password(request):
    sent = False
    if request.method == 'POST':
        form = EmailPasswordForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['email'] in User.objects.values_list('email', flat=True):
                # post_url = request.build_absolute_uri(post.get_absolute_url())
                subject = 'Password Reset'
                message_html = render_to_string('registration/password_reset_email.html')
                message = strip_tags(message_html)
                msg = EmailMultiAlternatives(subject, message_html, '', [cd['email']])
                msg.attach_alternative(message_html, "text/html")
                msg.send()
                # send_mail(subject, message, 'admin@myblog.com', [cd['to']])
                sent = True
                messages.success(request, 'Password has been reset successfully')
            else:
                messages.error(request, 'User doesn\'t exist')
        else:
            messages.error(request, 'User doesn\'t exist')
    else:
        form = EmailPasswordForm()
    return render(request, 'registration/password_reset_form.html', {'form': form, 'sent': sent})
