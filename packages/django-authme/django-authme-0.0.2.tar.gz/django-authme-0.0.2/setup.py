import re
from setuptools import setup, find_packages

file_content = None
with open('authme/__init__.py') as f:
    file_content = f.read()

search_for = lambda match: re.search(rf'^{match}\s*=\s*[\'"]([^\'"]*)[\'"]', file_content, re.MULTILINE).group(1)

name = search_for('__name__')
version = search_for('__version__')
author = search_for('__author__')
license = search_for('__license__')

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(
    name=name,
    version=version,
    description='Authentication utilities and systems for Django',
    long_description=readme,
    long_description_content_type='text/markdown',
    author=author,
    license=license,
    project_urls={
        'Source': 'https://github.com/legi0n/django-authme',
        'Issue tracker': 'https://github.com/legi0n/django-authme/issues',
    },
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        'django>=4.0'
    ],
    extras_require={
        'dev': [
            'twine',
            'wheel',
            'flake8',
            'mypy',

        ],
        'test': [
            'factory_boy',
            'Faker',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Framework :: Django',
        'Typing :: Typed',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords='django authentication login utilities',
)
