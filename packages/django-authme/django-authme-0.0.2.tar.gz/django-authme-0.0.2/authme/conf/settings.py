from django.conf import settings

__all__ = [
    'DEFAULTS',
    'app_settings',
]


DEFAULTS = {

    # Miscellaneous
    'DEFAULT_PERMISSION_DENIED_MESSAGE': 'Forbidden',


    # Signup
    'SIGNUP_ALLOWED': True,
    'POST_SIGNUP_LOGIN': False,
    'SIGNUP_URL': '/signup/',
    'SIGNUP_REDIRECT_URL': '/',
    'SIGNUP_DISALLOWED_URL': '/signup/closed/',
    'SIGNUP_REDIRECT_AUTHENTICATED_USER': True,

    # Login
    'LOGIN_URL': '/login/',
    'LOGIN_REDIRECT_URL': '/',
    'LOGIN_REDIRECT_AUTHENTICATED_USER': True,


    # Logout
    'LOGOUT_URL': '/logout/',
    'LOGOUT_REDIRECT_URL': '/',

}


class AppSettings:

    default_settings: dict = DEFAULTS

    def __getattr__(self, attr: str):
        if attr not in self.default_settings:
            raise AttributeError(f'Invalid setting: {attr}')
        try:
            value = getattr(settings, 'AUTHME', {})[attr]
        except KeyError:
            value = self.default_settings[attr]
        return value


app_settings = AppSettings()
