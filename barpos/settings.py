"""
Django settings for barpos project.

Generated by 'django-admin startproject' using Django 3.0.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_+($v8+m9z94kh4*dpz-xc%nd#11^gf9xp$rb^=@g7#l8_k46+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0','localhost','127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django.contrib.humanize',

    'accounts',
    'inventory',
    'pos',
    'reports',
    'quotations',

    'djmoney',
    'crispy_forms',
    'rest_framework',
    'jsonify',
    'bootstrap_modal_forms',
    'widget_tweaks',
    'sweetify',
    'django_countries',
    'django_filters',
    'dynamic_fields',
    'constance',
    'qrcode',
    'barcode',
    'phonenumber_field',
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

ROOT_URLCONF = 'barpos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'barpos.wsgi.application'

AUTH_USER_MODEL = 'accounts.CustomUser' # changes the built user model to ours



# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('POSTGRES_NAME'),
#         'USER': os.environ.get('POSTGRES_USER'),
#         'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
#         'HOST': 'db',
#         'PORT': 5432,
#     }
# }
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql', 
#         'NAME': 'bar_pos',
#         'USER': 'root',
#         'PASSWORD': 'root',
#         'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
#         'PORT': '3306',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Maseru'

USE_I18N = True

USE_THOUSAND_SEPERATOR = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
MEDIA_URL = '/images/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'accounts/static/images')

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_URL = 'login'
LOGOUT_URL ='logout'
LOGIN_REDIRECT_URL ='system_dashboard'

CURRENCIES = ('MWK',)

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    # 'PAGE_SIZE': 10
}

CONSTANCE_ADDITIONAL_FIELDS = {
'image_field': ['django.forms.ImageField', {}],
'float_field': ['django.forms.FloatField', {}],
'boolean_field': ['django.forms.BooleanField', {}],
'yes_no_null_select': ['django.forms.fields.ChoiceField', {'widget': 'django.forms.Select','choices': (("yes", "Yes"), ("no", "No"))
}],
}

CONSTANCE_CONFIG = {
'SHOP_NAME':('EPSILON BAR','You are Home!!' ),
'TAG_LINE':('The best in Town!!', 'The best Shop in Town'),
'ADDRESS':('P.O. Box 418','Address' ),
'LOCATION':('Lilongwe','Lilongwe' ),
'COUNTRY':('Malawi','Malawi' ),
'TEL':('+ 265 000 000',' Tel'),
'FAX':('+ 265 000 000',' Fax'),
'CEL':('+ 265 000 000',' Cel'),
'EMAIL':('mcatechmw@mcatech.mw','MCATECH'),
'TAX_NAME':(16.5,'VAT','float_field'),
'LOGO_IMAGE': ('images.png', 'Company logo', 'image_field'),
'SERVICE_FEE_A':(38.0,'FEE A','float_field'),
'SERVICE_FEE_B':(35.0,'FEE B','float_field'),
'SERVICE_FEE_C':(30.0,'FEE C','float_field'),
'ACCOUNT_NUMBER':('1234567890','ACCOUNT NUMBER'),
'QUICK_SALE': ('yes', 'QUICK_SALE', 'yes_no_null_select'),
}

CONSTANCE_CONFIG_FIELDSETS = {
'Shop Options': ('SHOP_NAME','LOGO_IMAGE','TAG_LINE','ADDRESS','LOCATION','TEL','FAX','EMAIL','CEL','COUNTRY'),
'Invoice Options': ('TAX_NAME','SERVICE_FEE_A','SERVICE_FEE_B', 'SERVICE_FEE_C'),
'Pos Settings':('QUICK_SALE','ACCOUNT_NUMBER',),
}

PHONENUMBER_DB_FORMAT = 'NATIONAL'
PHONENUMBER_DEFAULT_REGION = 'MW'