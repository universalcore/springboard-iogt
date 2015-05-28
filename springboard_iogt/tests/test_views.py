import re

from datetime import datetime, timedelta

from pyramid import testing

from springboard.tests import SpringboardTestCase

from springboard_iogt.views import IoGTViews
from springboard_iogt.application import main


class TestIoGTViews(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        self.config = testing.setUp(settings={
            'unicore.repos_dir': self.working_dir,
            'unicore.content_repo_urls': self.workspace.working_dir,
        })

    def tearDown(self):
        testing.tearDown()

    def test_index_view(self):
        [category] = self.mk_categories(self.workspace, count=1)
        [page] = self.mk_pages(
            self.workspace, count=1,
            created_at=datetime.utcnow().isoformat(),
            primary_category=category.uuid,
            featured=True)
        app = self.mk_app(self.workspace, main=main)
        re_page_url = re.compile(r'/page/.{32}/')
        re_category_url = re.compile(r'/category/.{32}/')

        response = app.get('/')
        self.assertEqual(response.status_int, 200)
        html = response.html
        self.assertEqual(len(html.find_all('a', href=re_page_url)), 1)
        self.assertEqual(len(html.find_all('a', href=re_category_url)), 2)

        page = page.update({'primary_category': None})
        self.workspace.save(page, 'Update page category')
        self.workspace.refresh_index()
        html = app.get('/').html
        self.assertEqual(len(html.find_all('a', href=re_page_url)), 1)
        self.assertEqual(len(html.find_all('a', href=re_category_url)), 0)
