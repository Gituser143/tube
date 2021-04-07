from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Name', max_length=100)
    password = forms.CharField(label='Password', max_length=100)


class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', max_length=100)
    email = forms.CharField(label='Email ID', max_length=100)
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)
