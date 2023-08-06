from django.contrib.auth import authenticate, get_user_model, login
from authme.conf.settings import app_settings
from authme._types import FormType, UserType
from authme.views import SignupView as BaseSignupView

__all__ = [
    'SignupView',
]


UserModel = get_user_model()


class SignupView(BaseSignupView):
    def process(self, form: FormType) -> UserType:
        user = form.save()
        user = authenticate(
            **{
                UserModel.USERNAME_FIELD: user.get_username(),
                'password': form.cleaned_data['password1'],
            }
        )

        if app_settings.POST_SIGNUP_LOGIN:
            login(self.request, user)
        return user
