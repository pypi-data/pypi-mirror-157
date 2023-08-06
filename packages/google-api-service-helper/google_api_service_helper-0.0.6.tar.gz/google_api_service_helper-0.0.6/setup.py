from pathlib import Path

from setuptools import setup

basedir = Path(__file__).parent

with open(basedir / 'README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='google_api_service_helper',
    version='0.0.6',
    description='A simple library for convenient work with the Google API for'
                ' Drive and Sheets',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/andy-takker/google-api-service-helper',
    platforms='any',
    install_requires=[
        'httplib2',
        'oauth2client',
        'google-api-python-client',
    ],
    packages=['google_api_service_helper'],
    author_email='sergey.natalenko@mail.ru',
    author='Sergey Natalenko',
    keywords='google api',
    license='GPL',
)
