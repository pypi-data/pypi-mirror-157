from typing import Union
from django.http.request import HttpRequest
from django.http.response import HttpResponseBase, HttpResponse
from django.forms import BaseForm, ModelForm
from django.contrib.auth.models import AbstractUser, AnonymousUser


HttpRequestType  = HttpRequest
HttpResponseType = Union[HttpResponseBase, HttpResponse]
FormType         = Union[BaseForm, ModelForm]
UserType         = AbstractUser
AnyUserType      = Union[AbstractUser, AnonymousUser]
