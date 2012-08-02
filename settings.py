USE_I18N = True

# Valid languages
LANGUAGES = (
    ('en', 'English'),
    ('ru_RU', 'Russian'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.i18n'
)

LANGUAGE_CODE = 'en'