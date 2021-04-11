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
from django.urls import reverse
from .models import Video, Comment, Playlist
from hashlib import sha256
import string
import random
import time
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
        most_liked_videos = Video.objects.order_by(
            '-num_likes').filter(Q(is_private=False) | Q(user_id=request.user.id))[:10]
        return render(request, self.template_name, {'most_recent_videos': most_recent_videos, 'most_liked_videos': most_liked_videos})

    def post(self, request):
        return HttpResponse('This is index view. POST request.')


class PlaylistIndexView(View):
    template_name = 'playlist_index.html'

    def get(self, request):
        # fetch videos from db
        most_recent_playlists = Playlist.objects.filter(
            Q(is_private=False) | Q(user_id=request.user.id)).order_by('name')[:10]
        return render(request, self.template_name, {'most_recent_playlists': most_recent_playlists})

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
            "video_type": video_by_id.path.split(".")[-1],
            "liked": False
        }

        liked_ids = video_by_id.likes
        if request.user.is_authenticated:
            if request.user.id in liked_ids:
                context['liked'] = True

        context['num_likes'] = video_by_id.num_likes

        if request.user.is_authenticated == True:
            comment_form = CommentForm()
            context['form'] = comment_form

        comments = Comment.objects.filter(
            video__id=id).order_by('-datetime')[:5]

        context['comments'] = comments
        return render(request, self.template_name, context)

    def post(self, request, id):
        try:
            video_by_id = Video.objects.get(id=id)
        except ObjectDoesNotExist:
            return render(request, "error.html", {'error': "Error: Invalid Video URL. Video does not exist!"})
        like = request.POST['like']

        if like == 'True':
            if request.user.id not in video_by_id.likes:
                video_by_id.likes.append(request.user.id)
        else:
            video_by_id.likes.remove(request.user.id)

        video_by_id.num_likes = len(video_by_id.likes)
        video_by_id.save()

        return HttpResponseRedirect('/video/{}'.format(id))


class PlaylistView(View):
    template_name = "playlist.html"

    def get(self, request, playlist_id):
        try:
            playlist_by_id = Playlist.objects.get(id=playlist_id)
        except ObjectDoesNotExist:
            return render(request, "error.html", {'error': "Error: Invalid Playlist URL. Playlist does not exist!"})
        video_ids = playlist_by_id.video_ids
        videos = Video.objects.filter(id__in=video_ids)
        context = {'videos': videos, 'playlist': playlist_by_id}
        return render(request, self.template_name, context)


class PlaylistVideoView(View):
    template_name = "playlist_video.html"

    def get(self, request, playlist_id, video_id):
        playlist_by_id = Playlist.objects.get(id=playlist_id)
        video_ids = playlist_by_id.video_ids
        videos = Video.objects.filter(id__in=video_ids)

        video_by_id = Video.objects.get(id=video_id)
        context = {
            'video': video_by_id,
            'videos': videos,
            'playlist': playlist_by_id,
            'video_type': video_by_id.path.split(".")[-1]
        }
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

            new_video = Video(
                title=title,
                description=description,
                user=request.user,
                path="/media/" + path,
                video=video,
                is_private=is_private,
                likes=[]
            )
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
            description = form.cleaned_data['description']
            user = request.user

            new_playlist = Playlist(
                name=name,
                is_private=is_private,
                user=user,
                description=description,
                video_ids=[]
            )

            new_playlist.save()

            # redirect to detail view template of a Video
            return render(request, "error.html", {'error': "Playlist Created!"})
        else:
            return render(request, "error.html", {'error': "Error: Inavlid Form Input!"})


class AddVideoToPlaylistView(View):
    template_name = "add_to_playlist.html"

    def get(self, request, id):
        # fetch playlists from db
        playlists = Playlist.objects.filter(
            user_id=request.user.id).order_by('name')
        video_id = id
        return render(request, self.template_name, {'playlists': playlists, 'video_id': video_id})

    def post(self, request, id):
        playlists = request.POST.getlist('checks[]')
        video_id = id
        for playlist in playlists:
            playlist_id = int(playlist)
            playlist_obj = Playlist.objects.get(id=playlist_id)
            video_list = playlist_obj.video_ids
            if video_id not in video_list:
                video_list.append(video_id)
            playlist_obj.video_ids = video_list
            playlist_obj.save()

        return HttpResponseRedirect('/')


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


class DeleteVideoView(View):
    template_name = "delete_video.html"

    def get(self, request, id):
        video_by_id = Video.objects.get(id=id)
        return render(request, self.template_name, {'video': video_by_id})

    def post(self, request, id):
        video_by_id = Video.objects.get(id=id)
        playlists = Playlist.objects.all()
        for playlist in playlists:
            video_ids = playlist.video_ids
            try:
                video_ids.remove(id)
            except:
                continue
            playlist.save()

        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        path = dir_path + video_by_id.path
        os.remove(path)

        video_by_id.delete()
        return render(request, "error.html", {'msg': "Video Deleted!"})


class RemoveVideoView(View):
    template_name = "remove_from_playlist.html"

    def get(self, request, id):
        playlist_by_id = Playlist.objects.get(id=id)
        video_ids = playlist_by_id.video_ids
        videos = Video.objects.filter(id__in=video_ids)
        context = {'videos': videos, 'playlist': playlist_by_id}
        return render(request, self.template_name, context)

    def post(self, request, id):
        videos = request.POST.getlist('checks[]')
        playlist_id = id
        playlist_obj = Playlist.objects.get(id=playlist_id)
        video_list = playlist_obj.video_ids
        for video in videos:
            video_id = int(video)
            try:
                video_list.remove(video_id)
            except:
                continue
        playlist_obj.video_ids = video_list
        playlist_obj.save()

        return HttpResponseRedirect('/playlist/{}'.format(playlist_id))


class DeletePlaylistView(View):
    template_name = "delete_playlist.html"

    def get(self, request, id):
        playlist_by_id = Playlist.objects.get(id=id)
        return render(request, self.template_name, {'playlist': playlist_by_id})

    def post(self, request, id):
        playlist_by_id = Playlist.objects.get(id=id)
        playlist_by_id.delete()

        return render(request, "error.html", {'msg': "Playlist Deleted!"})


class ErrorView(View):
    template_name = "error.html"
    error_string = "error"

    def get(self, request):
        return render(request, self.template_name, {'error': self.error_string})

    def setError(self, error_msg):
        self.error_string = error_msg
