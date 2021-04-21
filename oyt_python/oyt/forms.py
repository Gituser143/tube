# Copyright 2021 Bhargav SNV
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

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
    is_private = forms.BooleanField(label='Private', required=False)
    video = forms.FileField()


class EditVideoForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100, required=False)
    description = forms.CharField(
        label='Description', max_length=300, required=False)
    is_private = forms.BooleanField(label='Private', required=False)


class NewPlaylistForm(forms.Form):
    name = forms.CharField(label='Playlist Name', max_length=100)
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
