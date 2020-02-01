from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.views.decorators.http import require_POST
from .forms import CommentForm, SearchForm, StreamCreateForm
from .models import Stream
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from common.decorators import ajax_required
from django.http import JsonResponse, HttpResponse
from .documents import StreamIndex
from taggit.models import Tag
from requests import Session
import json


@login_required
def my_stream_list(request, tag_slug=None):
    my_streams = Stream.objects.all()
    all_res = []
    for stream in my_streams:
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
    paginator = Paginator(all_res, 5)
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
                  'streams/my_stream_list.html',
                  {'section': 'streams', 'streams': all_res})


@login_required
def stream_list(request):
    clientId= "yx253jsyhtua7kycwmhpnxja32qqm8"  #Register a Twitch Developer application and put its client ID here
    apiRequestUrl="https://api.twitch.tv/helix/streams"
    session = Session()
    response = session.get(apiRequestUrl, headers={
    'Client-ID': clientId,
    'Accept': 'application/vnd.twitchtv.v5+json',
    'Content-Type': 'application/json'
    })
    session = Session()
    streams = json.loads(response.text)
    streams = streams['data']
    for i in range(len(streams)):
        path = 'http://127.0.0.1:8000/stream_details/' + streams[i]['user_id']
        streams[i]['path'] = path
        streams[i]['thumbnail_url'] = streams[i]['thumbnail_url'].replace("{width}x{height}", "250x250")
        print(streams[i])

    page = request.GET.get('page', 1)
    paginator = Paginator(streams, 5)
    try:
        streams = paginator.page(page)
    except PageNotAnInteger:
        streams = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        streams = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'streams/streams_list_ajax.html',
                      {'section': 'streams', 'streams': streams})
    return render(request,
                  'streams/streams_list.html',
                  {'section': 'streams', 'streams': streams})


@login_required
def following_book(request, tag_slug=None):
    users = request.user.following.all
    my_streams = Stream.objects.all().filter(user__in=users)
    all_res = []
    for stream in my_streams:
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
    paginator = Paginator(all_res, 5)
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
                  'accounts/dashboard.html',
                  {'section': 'streams', 'streams': all_res})


@ajax_required
@login_required
@require_POST
def stream_like(request):
    stream_id = request.POST.get('id')
    action = request.POST.get('action')
    if stream_id and action:
        try:
            stream = Stream.objects.get(id=stream_id)
            if action == 'like':
                stream.users_like.add(request.user)
            else:
                stream.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Stream.DoesNotExist:
            pass
    return JsonResponse({'status': 'ko'})


@login_required()
def stream_create(request):
    if request.method == 'POST':
        form = StreamCreateForm(request.POST)
        # publisher_from = PublisherForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            form.save_m2m()
            # publisher_from.save()
            messages.success(request, 'Stream added successfully')
            return redirect(new_item.get_absolute_url())
    else:
        form = StreamCreateForm(data=request.GET)
        # publisher_from = PublisherForm(data=request.GET)

    return render(request, 'streams/create_stream.html', {'section': 'streams',
                                                       'form': form})


@login_required()
def my_stream_detail(request, user_name):
    stream = get_object_or_404(Stream, user_name=user_name)
    username = getattr(stream, 'user_name')
    user = request.user
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
    return render(request,
                  'streams/stream_detail.html',
                  {'section': 'streams',
                   'stream': stream,
                   'user': user,
                   })

@login_required()
def stream_detail(request, user_id):
    clientId= "yx253jsyhtua7kycwmhpnxja32qqm8"
    apiRequestUrl = 'https://api.twitch.tv/kraken/channels/'+user_id
    session = Session()
    response = session.get(apiRequestUrl, headers={
    'Client-ID': clientId,
    'Accept': 'application/vnd.twitchtv.v5+json',
    'Content-Type': 'application/json'
    })
    stream = json.loads(response.text)
    return render(request,
                  'streams/stream_detail.html',
                  {'section': 'streams',
                   'stream': stream,
                   })

        
def stream_search(request):
    sform = SearchForm()
    if 'name' in request.GET:
        sform = SearchForm(request.GET)
        if sform.is_valid():
            cd = sform.cleaned_data
            results = StreamIndex.search().query("match", user_name=cd['name'])
            total_results = results.count()
        all_res = []
        for res in results:
            clientId= "yx253jsyhtua7kycwmhpnxja32qqm8"
            apiRequestUrl = 'https://api.twitch.tv/kraken/users?login='+res.user_name
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
            print(stream)
            banner = stream['video_banner']
            if banner is None:
                banner = "C:/Users/ajava/Desktop/streaming.png"
            current_res = {
                'user_name' : res.user_name,
                'url' : res.url,
                'banner' : banner
            }
            all_res.append(current_res)


        return render(request, 'streams/stream_search.html', {'sform': sform,
                                                           'cd': cd,
                                                           'results': all_res,
                                                           'total_results': total_results})
    else:

        return render(request, 'streams/stream_search.html', {'sform': sform})