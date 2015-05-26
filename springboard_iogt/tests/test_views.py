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

    def test_recent_content(self):
        category_p1, category_p3 = self.mk_categories(self.workspace, count=2)
        [page1] = self.mk_pages(
            self.workspace, count=1,
            primary_category=category_p1.uuid,
            created_at=datetime.utcnow().isoformat())
        [page2] = self.mk_pages(
            self.workspace, count=1,
            primary_category=None,
            created_at=(datetime.utcnow() - timedelta(hours=1)).isoformat())
        [page3] = self.mk_pages(
            self.workspace, count=1,
            primary_category=category_p3.uuid,
            created_at=(datetime.utcnow() - timedelta(hours=2)).isoformat())
        views = IoGTViews(self.mk_request())

        results = views.recent_content()(limit=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(
            {(category_p1.uuid, page1.uuid), (None, page2.uuid)},
            set((c.uuid if c else None, p.uuid) for c, p in results))

        results = views.recent_content()(limit=3)
        self.assertEqual(len(results), 3)
        self.assertEqual(
            {(category_p1.uuid, page1.uuid), (None, page2.uuid),
             (category_p3.uuid, page3.uuid)},
            set((c.uuid if c else None, p.uuid) for c, p in results))

    def test_index_view(self):
        [category] = self.mk_categories(self.workspace, count=1)
        [page1, page2] = self.mk_pages(
            self.workspace, count=2,
            created_at=datetime.utcnow().isoformat())
        page1 = page1.update({'primary_category': category.uuid})
        self.workspace.save(page1, 'Update page category')
        self.workspace.refresh_index()
        app = self.mk_app(self.workspace, main=main)

        response = app.get('/')
        self.assertEqual(response.status_int, 200)
        html = response.html
        re_page_url = re.compile(r'/page/.{32}/')
        re_category_url = re.compile(r'/category/.{32}/')
        self.assertEqual(len(html.find_all('a', href=re_page_url)), 2)
        self.assertEqual(len(html.find_all('a', href=re_category_url)), 2)
