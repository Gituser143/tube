from django.shortcuts import render
from django.views.generic.base import View, HttpResponse, HttpResponseRedirect
from .forms import LoginForm
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.


class HomeView(View):
    template_name = 'index.html'

    def get(self, request):
        variableA = 'Title'
        return render(request, self.template_name, {'variableA': variableA})

    def post(self, request):
        return HttpResponse('This is index view. POST request.')


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        return HttpResponse('This is login view. POST request.')


class RegisterView(View):
    template_name = "register.html"

    def get(self, request):
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

        return HttpResponse('This is register view. POST request.')


class NewVideo(View):
    template_name = 'new_video.html'

    def get(self, request):
        variableA = 'New Video'
        return render(request, self.template_name, {'variableA': variableA})

    def post(self, request):
        return HttpResponse('This is index view. POST request.')


class ErrorView(View):
    template_name = "error.html"
    error_string = "error"

    def get(self, request):
        return render(request, self.template_name, {'error': self.error_string})

    def setError(self, error_msg):
        self.error_string = error_msg
