from django.contrib.auth import login
from authme._types import FormType, UserType
from authme.views import LoginView as BaseLoginView

__all__ = [
    'LoginView',
]


class LoginView(BaseLoginView):
    def process(self, form: FormType) -> UserType:
        user = form.get_user()
        login(self.request, user)
        return user
