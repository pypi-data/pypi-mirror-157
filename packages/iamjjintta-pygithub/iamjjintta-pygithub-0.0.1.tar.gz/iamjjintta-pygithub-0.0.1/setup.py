
from setuptools import setup
from setuptools import find_packages


with open('README.md') as readme:
    long_description = readme.read()


setup(
    name             = 'iamjjintta-pygithub',
    version          = '0.0.1',
    author           = 'iam-jjintta',
    author_email     = 'iamjjintta@gmail.com',
    description      = 'Simple GitHub API with Python',
    long_description = long_description,
    long_description_content_type='text/markdown',
    url              = 'https://github.com/iamjjintta-python/PyGitHub',
    download_url     = 'https://github.com/iamjjintta-python/PyGitHub',
    license          = 'Apache License 2.0',
    license_files    = [ 'LICENSE' ],
    packages         = find_packages(),
    zip_safe         = False,
    install_requires = [
        'beautifulsoup4==4.11.1',
        'bs4==0.0.1',
        'certifi==2022.6.15',
        'charset-normalizer==2.1.0',
        'cssselect==1.1.0',
        'idna==3.3',
        'lxml==4.9.1',
        'requests==2.28.1',
        'soupsieve==2.3.2.post1',
        'urllib3==1.26.9'
    ],
    classifiers      = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
)
