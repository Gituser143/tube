from django.shortcuts import render
from django.views.generic.base import View, HttpResponse, HttpResponseRedirect
from .forms import LoginForm
from .forms import RegisterForm
from .forms import NewVideoForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, authenticate, logout
from .models import Video, Comment
from hashlib import sha256
import string
import random
import time
# Create your views here.


class HomeView(View):
    template_name = 'index.html'

    def get(self, request):
        # fetch videos from db
        most_recent_videos = Video.objects.order_by('-datetime')[:10]
        return render(request, self.template_name, {'most_recent_videos': most_recent_videos})

    def post(self, request):
        return HttpResponse('This is index view. POST request.')


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            return HttpResponseRedirect('/login')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(
                request=request,
                username=username,
                password=password
            )

            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return render(request, "error.html", {'error': "Error: Invalid Credentials!"})

        return HttpResponseRedirect('/')


class RegisterView(View):
    template_name = "register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Create Account
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            # Verify Unique User
            try:
                existing_user = User.objects.get(username=username)
                if existing_user is not None:
                    return render(request, "error.html", {'error': "Error: Username is already taken!"})

            except ObjectDoesNotExist:
                pass

            # Verify Unique Email ID
            try:
                existing_email = User.objects.get(email=email)
                if existing_email is not None:
                    return render(request, "error.html", {'error': "Error: Email ID is already in use!"})
            except ObjectDoesNotExist:
                pass

            # Create object
            new_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            # Hash and set password
            new_user.set_password(password)

            # Save user
            new_user.save()
            return HttpResponseRedirect('/login')
        else:
            return render(request, "error.html", {'error': "Error: Inavlid Form Input!"})


class NewVideoView(View):
    template_name = 'new_video.html'
    supported_types = ['video/mp4', 'video/x-matroska', 'video/webm']

    def get(self, request):
        if request.user.is_authenticated == False:
            return HttpResponseRedirect('/login')
        form = NewVideoForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = NewVideoForm(request.POST, request.FILES)
        if form.is_valid():
            # create a new Video Entry
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            video = form.cleaned_data['video']

            if video.content_type not in self.supported_types:
                return render(request, "error.html", {'error': "Error: Inavlid Video format {}!".format(video.content_type)})

            hash_str = str(round(time.time() * 1000)) + \
                str(video.name) + str(request.user)

            hash = sha256(hash_str.encode())
            path = hash.hexdigest()[:10] + "_" + video.name

            new_video = Video(title=title,
                              description=description,
                              user=request.user,
                              path=path)
            new_video.save()

            # redirect to detail view template of a Video
            return HttpResponseRedirect('/video/{id}'.format(id=new_video.id))
        else:
            return render(request, "error.html", {'error': "Error: Inavlid Form Input!"})


class ErrorView(View):
    template_name = "error.html"
    error_string = "error"

    def get(self, request):
        return render(request, self.template_name, {'error': self.error_string})

    def setError(self, error_msg):
        self.error_string = error_msg
