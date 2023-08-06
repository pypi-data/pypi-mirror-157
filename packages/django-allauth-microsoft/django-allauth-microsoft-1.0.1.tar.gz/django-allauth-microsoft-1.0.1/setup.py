from setuptools import setup, find_packages

setup(
    name = "django-allauth-microsoft",
    version = "1.0.1",
    author = "Muhammed Mehmood",
    author_email = "ifreezeu2@gmail.com",
    description = "Microsoft OAuth2 provider for django-allauth",
    url = "https://github.com/schaenzer/django-allauth-microsoft",
    packages=find_packages(),
    install_requires=['django-allauth>=0.34.0'],
    classifiers = [
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)
