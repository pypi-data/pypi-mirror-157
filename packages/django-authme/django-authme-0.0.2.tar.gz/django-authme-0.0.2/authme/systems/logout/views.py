from django.contrib.auth import logout
from authme.views import LogoutView as BaseLogoutView

__all__ = [
    'LogoutView',
]


class LogoutView(BaseLogoutView):
    def process(self) -> None:
        logout(self.request)
