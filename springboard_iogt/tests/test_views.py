import re
from urllib import urlencode
from datetime import datetime

from pyramid import testing

from mock import patch

from springboard.tests import SpringboardTestCase

from springboard_iogt.views import (
    PERSONAE, PERSONA_COOKIE_NAME, PERSONA_SKIP_COOKIE_VALUE)
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
        app.set_cookie(PERSONA_COOKIE_NAME, PERSONA_SKIP_COOKIE_VALUE)

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

    def test_persona_tween(self):
        app = self.mk_app(self.workspace, main=main)

        response = app.get('/')
        self.assertEqual(response.status_int, 302)
        self.assertTrue(
            response.location.startswith('http://localhost/persona/'))

        response = app.get('/persona/')
        self.assertEqual(response.status_int, 200)

        response = app.get('/matches/nothing/', expect_errors=True)
        self.assertEqual(response.status_int, 404)

        self.mk_pages(
            self.workspace, count=2,
            created_at=datetime.utcnow().isoformat())  # sets up mapping
        app.set_cookie(PERSONA_COOKIE_NAME, PERSONA_SKIP_COOKIE_VALUE)
        response = app.get('/')
        self.assertEqual(response.status_int, 200)

        for slug in ('child', 'skip'):
            app.reset()
            response = app.get('/persona/%s/' % slug)
            self.assertEqual(response.status_int, 302)
            self.assertEqual(response.location, 'http://localhost/')

    def test_select_persona(self):
        app = self.mk_app(self.workspace, main=main)
        next_url = 'http://localhost/page/1234/'
        querystring = urlencode({'next': next_url})

        response = app.get('/persona/worker/?%s' % querystring)
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.location, next_url)
        cookie = response.headers.get('Set-Cookie', '')
        self.assertIn('%s=WORKER;' % PERSONA_COOKIE_NAME, cookie)

        response = app.get('/persona/not-a-persona/', expect_errors=True)
        self.assertEqual(response.status_int, 404)

    @patch('springboard.events.pageview.delay')
    def test_track_persona_on_ga(self, mocked_pageview):
        app = self.mk_app(
            self.workspace,
            main=main,
            settings={'ga.profile_id': 'ID-000',
                      'ga.persona_dimension_id': 'dimension0'})
        app.get('/persona/worker/')
        ga_data = mocked_pageview.call_args[0][2]
        self.assertIn('dimension0', ga_data)
        self.assertEqual(ga_data['dimension0'], 'WORKER')

    def test_skip_persona_selection(self):
        app = self.mk_app(self.workspace, main=main)
        next_url = 'http://localhost/page/1234/'
        querystring = urlencode({'next': next_url})

        response = app.get('/persona/skip/?%s' % querystring)
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.location, next_url)
        cookie = response.headers.get('Set-Cookie', '')
        self.assertIn(
            '%s=%s;' % (PERSONA_COOKIE_NAME, PERSONA_SKIP_COOKIE_VALUE),
            cookie)

    def test_personae(self):
        app = self.mk_app(self.workspace, main=main)
        url = 'http://localhost/page/1234/'
        querystring = urlencode({'next': url})

        html = app.get(url).follow().html
        persona_url_tags = html.find_all('a', href=re.compile(
            r'/persona/(%s)/' % '|'.join(p.lower() for p in PERSONAE)))
        skip_url_tags = html.find_all('a', href=re.compile(r'/persona/skip/'))
        self.assertEqual(len(persona_url_tags), 4)
        self.assertEqual(len(skip_url_tags), 1)
        self.assertTrue(all(querystring in tag['href']
                            for tag in persona_url_tags))
        self.assertTrue(querystring in skip_url_tags[0]['href'])
