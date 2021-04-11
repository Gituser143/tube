from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Name', max_length=100)
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput, max_length=100)


class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput, max_length=100)
    email = forms.CharField(label='Email ID', max_length=100)
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)


class CommentForm(forms.Form):
    text = forms.CharField(label='text', max_length=300)


class NewVideoForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    description = forms.CharField(label='Description', max_length=300)
    is_private = forms.BooleanField(label='Private')
    video = forms.FileField()


class NewPlaylistForm(forms.Form):
    name = forms.CharField(label='Playlist Name', max_length=100)
    is_private = forms.BooleanField(label='Private', required=False)


class EditVideoForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100, required=False)
    description = forms.CharField(
        label='Description', max_length=300, required=False)
    is_private = forms.BooleanField(label='Private', required=False)


class EditUserForm(forms.Form):
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput, max_length=100, required=False)
    first_name = forms.CharField(
        label='First Name', max_length=100, required=False)
    last_name = forms.CharField(
        label='Last Name', max_length=100, required=False)
