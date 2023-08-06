
import requests

from urllib.parse import urljoin
from bs4 import BeautifulSoup


class GitHub:

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url_main = 'https://www.github.com/'
    url_raw = 'https://raw.githubusercontent.com/'
    url_session = 'https://github.com/session/'


    def __init__(self, email_or_username=None, password=None):
        username = email_or_username
        if username and password:
            self.username = username
            self.password = password
        self.session = requests.Session()


    def get_authenticity_token(self):
        session_page = self.session.get(self.url_session, headers=self.headers)
        soup = BeautifulSoup(session_page.text, 'lxml')
        attrs = { 'name': 'authenticity_token' }
        token = soup.find('input', attrs=attrs)['value']
        return token


    def login(self):
        token = self.get_authenticity_token()
        data = {
            'login': self.username,
            'password': self.password,
            'authenticity_token': token
        }
        result = self.session.post(self.url_session, data=data, headers=self.headers)
        return result


    def get_content(self, owner, repo, branch, path):
        prefix = '/'.join((owner, repo, branch, path))
        url = urljoin(self.url_raw, prefix)
        result = self.session.get(url, headers=self.headers)
        return result.content
