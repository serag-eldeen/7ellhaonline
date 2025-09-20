"""
Django settings for interactive_math_quiz project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# --- PRODUCTION SETTINGS ---

# SECRET_KEY is now read from an environment variable for security
# Make sure you set this on the PythonAnywhere "Web" tab
SECRET_KEY = os.environ.get('SECRET_KEY')

# DEBUG must be False on a live server
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
# Add your PythonAnywhere domain name here
ALLOWED_HOSTS = ['7ellhaonline.pythonanywhere.com']


# --- Application definition ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.core.apps.CoreConfig',
    'apps.users.apps.UsersConfig',
    'apps.academics.apps.AcademicsConfig',
    'apps.quizzes.apps.QuizzesConfig',
    'apps.dashboard.apps.DashboardConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'interactive_math_quiz.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'interactive_math_quiz.wsgi.application'


# --- Database ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# --- Internationalization ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- Static and Media Files ---

STATIC_URL = 'static/'
# This is where Django will COLLECT all static files for deployment.
STATIC_ROOT = BASE_DIR / "staticfiles"
# This is where Django looks for your static files during development.
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# --- Other Settings ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'users:redirect_after_login'
LOGOUT_REDIRECT_URL = '/'

# Add your domain here for security when using HTTPS
CSRF_TRUSTED_ORIGINS = ['https://7ellhaonline.pythonanywhere.com']