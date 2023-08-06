from typing import Optional, Callable, Any
from urllib.parse import urlparse
from django.shortcuts import resolve_url
from django.http.response import HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from authme.conf.settings import app_settings
from authme._types import (
    HttpRequestType,
    HttpResponseType,
)

__all__ = [
    'LoginRequiredMixin',
    'AnonymousRequiredMixin',
    'StaffUserRequiredMixin',
    'SuperUserRequiredMixin',
    'UserPassesTestMixin',
]


class AccessMixin:
    """
    Base access mixin. All access mixins should inherit from this one.
    """
    login_url: Optional[str] = None
    permission_denied_message: Optional[str] = None
    raise_exception: bool = False
    redirect_field_name: str = REDIRECT_FIELD_NAME

    def get_login_url(self) -> str:
        login_url = self.login_url or app_settings.LOGIN_URL
        if not login_url:
            class_name = self.__class__.__name__
            raise ImproperlyConfigured(
                f'{class_name} is missing the login_url attribute. Define '
                f'{class_name}.login_url, `LOGIN_URL` in settings.AUTHME, '
                f'or override {class_name}.get_login_url().'
            )
        return str(login_url)

    def get_permission_denied_message(self) -> str:
        permission_denied_message = (
            self.permission_denied_message
            or app_settings.DEFAULT_PERMISSION_DENIED_MESSAGE
        )
        if not permission_denied_message:
            class_name = self.__class__.__name__
            raise ImproperlyConfigured(
                f'{class_name} is missing the permission_denied_message '
                f'attribute. Define {class_name}.permission_denied_message, '
                f'`PERMISSION_DENIED_MESSAGE` in settings.AUTHME, or override '
                f'{class_name}.get_permission_denied_message().'
            )
        return str(permission_denied_message)

    def get_redirect_field_name(self) -> str:
        return self.redirect_field_name

    def handle_no_permission(
        self,
        message: Optional[str] = None
    ) -> HttpResponseType:
        if self.raise_exception or self.request.user.is_authenticated:
            message = message or self.get_permission_denied_message()
            raise PermissionDenied(message)

        path = self.request.build_absolute_uri()
        resolved_login_url = resolve_url(self.get_login_url())
        login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if (not login_scheme or login_scheme == current_scheme) and (
            not login_netloc or login_netloc == current_netloc
        ):
            path = self.request.get_full_path()
        return redirect_to_login(
            path,
            resolved_login_url,
            self.get_redirect_field_name(),
        )


class LoginRequiredMixin(AccessMixin):
    """
    Requires the user to be authenticated.
    """
    def dispatch(
        self,
        request: HttpRequestType,
        *args: Any,
        **kwargs: Any
    ) -> HttpResponseType:
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AnonymousRequiredMixin(AccessMixin):
    """
    Requires the user to be unauthenticated.
    """
    authenticated_redirect_url: Optional[str] = None

    def get_authenticated_redirect_url(self) -> str:
        authenticated_redirect_url: str = (
            self.authenticated_redirect_url
            or app_settings.LOGIN_REDIRECT_URL
        )
        return str(authenticated_redirect_url)

    def handle_no_permission(
        self,
        message: Optional[str] = None
    ) -> HttpResponseType:
        url = self.get_authenticated_redirect_url()
        if url == self.request.get_full_path():
            class_name = self.__class__.__name__
            raise ImproperlyConfigured(
                f'Circular redirect discovered. Please edit the '
                f'{class_name}.authenticated_redirect_url attribute, '
                f'`LOGIN_REDIRECT_URL` in settings.AUTHME, or override '
                f'{class_name}.get_authenticated_redirect_url().'
            )
        return HttpResponseRedirect(url)

    def dispatch(
        self,
        request: HttpRequestType,
        *args: Any,
        **kwargs: Any
    ) -> HttpResponseType:
        if request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class StaffUserRequiredMixin(AccessMixin):
    """
    Requires the user to be authenticated and a staffuser.
    """
    def dispatch(
        self,
        request: HttpRequestType,
        *args: Any,
        **kwargs: Any
    ) -> HttpResponseType:
        if not (request.user.is_staff or request.user.is_superuser):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class SuperUserRequiredMixin(AccessMixin):
    """
    Requires the user to be authenticated and a superuser.
    """
    def dispatch(
        self,
        request: HttpRequestType,
        *args: Any,
        **kwargs: Any
    ) -> HttpResponseType:
        if not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class UserPassesTestMixin(AccessMixin):
    """
    User must pass a test before being allowed access to the view.
    """
    def test_func(self, user) -> Any:
        class_name = self.__class__.__name__
        raise NotImplementedError(
            f'{class_name} is missing implementation of the '
            '`test_func` method. A function to test the user is required.'
        )

    def get_test_func(self) -> Callable[..., Any]:
        return self.test_func

    def dispatch(
        self,
        request: HttpRequestType,
        *args: Any,
        **kwargs: Any
    ) -> HttpResponseType:
        user_test_result = self.get_test_func()(request.user)
        if not user_test_result:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
