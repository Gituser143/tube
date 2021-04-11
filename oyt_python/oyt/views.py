from django.shortcuts import render
from django.views.generic.base import View, HttpResponse, HttpResponseRedirect
from .forms import LoginForm
from .forms import RegisterForm
from .forms import NewVideoForm
from .forms import CommentForm
from .forms import EditVideoForm
from .forms import EditUserForm
from .forms import NewPlaylistForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q
from .models import Video, Comment, Playlist
from hashlib import sha256
import string
import random
import time


class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return HttpResponseRedirect('/')


class HomeView(View):
    template_name = 'index.html'

    def get(self, request):
        # fetch videos from db
        most_recent_videos = Video.objects.order_by(
            '-datetime').filter(Q(is_private=False) | Q(user_id=request.user.id))[:10]
        return render(request, self.template_name, {'most_recent_videos': most_recent_videos})

    def post(self, request):
        return HttpResponse('This is index view. POST request.')


class VideoView(View):
    template_name = "video.html"

    def get(self, request, id):
        try:
            video_by_id = Video.objects.get(id=id)
        except ObjectDoesNotExist:
            return render(request, "error.html", {'error': "Error: Invalid Video URL. Video does not exist!"})

        context = {
            "video": video_by_id,
            "video_type": video_by_id.path.split(".")[-1]
        }

        if request.user.is_authenticated == True:
            comment_form = CommentForm()
            context['form'] = comment_form

        comments = Comment.objects.filter(
            video__id=id).order_by('-datetime')[:5]

        context['comments'] = comments
        return render(request, self.template_name, context)


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


class CommentView(View):
    template_name = "comment.html"

    def post(self, request):
        form = CommentForm(request.POST)
        if form.is_valid():
            # Create Comment
            comment = form.cleaned_data['text']
            video_id = request.POST['video']
            video = Video.objects.get(id=video_id)

            new_comment = Comment(
                user=request.user,
                text=comment,
                video=video
            )

            new_comment.save()

            return HttpResponseRedirect('/video/{}'.format(str(video_id)))
        else:
            return render(request, "error.html", {'error': "Error: Inavlid Form Input!"})


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
    supported_types = ['video/mp4', 'video/webm']

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
            is_private = form.cleaned_data['is_private']

            if video.content_type not in self.supported_types:
                return render(request, "error.html", {'error': "Error: Inavlid Video format {}!".format(video.content_type)})

            hash_str = str(round(time.time() * 1000)) + \
                str(video.name) + str(request.user)

            hash = sha256(hash_str.encode())
            path = hash.hexdigest()[:10] + "_" + video.name
            video.name = path

            new_video = Video(title=title,
                              description=description,
                              user=request.user,
                              path="/media/" + path,
                              video=video,
                              is_private=is_private)
            new_video.save()

            # redirect to detail view template of a Video
            return HttpResponseRedirect('/video/{id}'.format(id=new_video.id))
        else:
            return render(request, "error.html", {'error': "Error: Inavlid Form Input!"})


class CreatePlaylistView(View):
    template_name = "new_playlist.html"

    def get(self, request):
        if request.user.is_authenticated == False:
            return HttpResponseRedirect('/login')
        form = NewPlaylistForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = NewPlaylistForm(request.POST, request.FILES)
        if form.is_valid():
            # create a new Playlist Entry
            name = form.cleaned_data['name']
            is_private = form.cleaned_data['is_private']
            user = request.user

            new_playlist = Playlist(
                name=name,
                is_private=is_private,
                user=user,
                video_ids=[]
            )

            new_playlist.save()

            # redirect to detail view template of a Video
            return render(request, "error.html", {'error': "Playlist Created!"})
        else:
            return render(request, "error.html", {'error': "Error: Inavlid Form Input!"})


class EditVideoView(View):
    template_name = "edit_video.html"

    def get(self, request, id):
        if request.user.is_authenticated == False:
            return HttpResponseRedirect('/login')
        form = EditVideoForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, id):
        form = EditVideoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                video_by_id = Video.objects.get(id=id)
            except ObjectDoesNotExist:
                return render(request, "error.html", {'error': "Error: Invalid Video URL. Video does not exist!"})

            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            is_private = form.cleaned_data['is_private']

            if title != '':
                video_by_id.title = title

            if description != '':
                video_by_id.description = description

            if is_private == True or is_private == False:
                video_by_id.is_private = is_private

            video_by_id.save()
            return HttpResponseRedirect('/video/{id}'.format(id=video_by_id.id))
        else:
            return render(request, "error.html", {'error': "Error: Inavlid Form Input!"})


class EditUserView(View):
    template_name = "edit_user.html"

    def get(self, request):
        if request.user.is_authenticated == False:
            return HttpResponseRedirect('/login')
        form = EditUserForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = EditUserForm(request.POST, request.FILES)
        id = request.user.id
        if form.is_valid():
            try:
                user_by_id = User.objects.get(id=id)
            except ObjectDoesNotExist:
                return render(request, "error.html", {'error': "Error: Invalid user ID. User does not exist!"})

            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            if password != '':
                user_by_id.set_password(password)

            if first_name != '':
                user_by_id.first_name = first_name

            if last_name != '':
                user_by_id.last_name = last_name

            user_by_id.save()
            return HttpResponseRedirect('/')
        else:
            return render(request, "error.html", {'error': "Error: Inavlid Form Input!"})


class ErrorView(View):
    template_name = "error.html"
    error_string = "error"

    def get(self, request):
        return render(request, self.template_name, {'error': self.error_string})

    def setError(self, error_msg):
        self.error_string = error_msg
