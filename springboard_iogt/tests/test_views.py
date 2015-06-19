import re
from urllib import urlencode
from datetime import datetime

from pyramid import testing

from mock import patch

from springboard.tests import SpringboardTestCase

from springboard_iogt.views import (
    PERSONAE, PERSONA_COOKIE_NAME, PERSONA_SKIP_COOKIE_VALUE)
from springboard_iogt.application import main
from springboard_iogt.utils import ContentSection


class TestIoGTViews(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        self.config = testing.setUp(settings={
            'unicore.repos_dir': self.working_dir,
            'unicore.content_repos': self.workspace.working_dir,
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
        re_section_url = re.compile(r'/section/\w+/')
        app.set_cookie(PERSONA_COOKIE_NAME, PERSONA_SKIP_COOKIE_VALUE)

        response = app.get('/')
        self.assertEqual(response.status_int, 200)
        html = response.html
        self.assertEqual(len(html.find_all('a', href=re_page_url)), 1)
        self.assertEqual(len(html.find_all('a', href=re_section_url)), 5)

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
        self.assertEqual(ga_data['path'], '/persona/worker/')

        app.get('/not/here/', expect_errors=True)
        ga_data = mocked_pageview.call_args[0][2]
        self.assertEqual(ga_data['path'], '/not/here/?persona=WORKER')

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

    def test_content_section(self):
        ffl_workspace = self.mk_workspace(name='ffl')
        [category] = self.mk_categories(
            ffl_workspace, count=1, position=1)
        [page] = self.mk_pages(
            ffl_workspace, count=1, position=1,
            created_at=datetime.utcnow().isoformat(),
            primary_category=category.uuid)
        app = self.mk_app(self.workspace, main=main, settings={
            'unicore.content_repos': '\n'.join([self.workspace.working_dir,
                                                ffl_workspace.working_dir])
        })
        app.set_cookie(PERSONA_COOKIE_NAME, PERSONA_SKIP_COOKIE_VALUE)

        response = app.get('/section/doesnotexist/', expect_errors=True)
        self.assertEqual(response.status_int, 404)
        response = app.get('/section/ffl/')
        self.assertEqual(response.status_int, 200)

    def test_content_section_listing(self):
        app = self.mk_app(self.workspace, main=main)
        html = app.get('/does/not/exists/', expect_errors=True).html
        section_url_tags = html.find_all('a', href=re.compile(
            r'/section/(%s)/' % '|'.join(ContentSection.SLUGS)))
        self.assertEqual(len(section_url_tags), len(ContentSection.SLUGS))

    def test_language_visibility(self):
        settings = {
            'featured_languages': 'eng_GB\nlug_UG',
            'available_languages': 'eng_GB\nlug_UG'
        }
        app = self.mk_app(self.workspace, main=main, settings=settings)
        html = app.get('/does/not/exist/', expect_errors=True).html
        lang_el = html.find('div', class_='lang')
        self.assertIn('English', lang_el.text)
        self.assertIn('Luganda', lang_el.text)

        settings['available_languages'] = 'eng_GB'
        app = self.mk_app(self.workspace, main=main, settings=settings)
        html = app.get('/does/not/exist/', expect_errors=True).html
        self.assertFalse(html.find('div', class_='lang'))

    def test_about(self):
        app = self.mk_app(self.workspace, main=main)
        response = app.get('/about/')
        self.assertEqual(response.status_int, 200)
        response = app.get('/about/__LOCALE__=swa_TZ', expect_errors=True)
        self.assertEqual(response.status_int, 404)
