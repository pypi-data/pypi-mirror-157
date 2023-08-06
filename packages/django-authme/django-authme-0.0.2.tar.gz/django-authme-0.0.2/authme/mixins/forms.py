from typing import Optional
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.exceptions import ImproperlyConfigured

__all__ = [
    'RedirectURLMixin',
]


class RedirectURLMixin:
    next_page: Optional[str] = None
    redirect_field_name: str = REDIRECT_FIELD_NAME
    success_url_allowed_hosts: set = set()

    def get_success_url(self) -> str:
        return self.get_redirect_url() or self.get_default_redirect_url()

    def get_redirect_url(self) -> str:
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name)
        )
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ""

    def get_success_url_allowed_hosts(self) -> set:
        return {self.request.get_host(), *self.success_url_allowed_hosts}

    def get_default_redirect_url(self) -> str:
        """Return the default redirect URL."""
        if self.next_page:
            return resolve_url(self.next_page)
        raise ImproperlyConfigured(
            'No URL to redirect to. Provide a next_page.'
        )
