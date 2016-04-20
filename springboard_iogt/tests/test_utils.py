from pyramid import testing

from pyramid.i18n import make_localizer

from springboard.tests import SpringboardTestCase

from springboard_iogt.utils import ContentSection
from springboard_iogt.views import IoGTViews


class TestUtils(SpringboardTestCase):

    def tearDown(self):
        testing.tearDown()

    def serialize_section(self, section):
        return {
            'slug': section.slug,
            'data': section.data,
            'banner_url': section.banner_url,
            'title': section.title,
            'owner': section.owner,
            'descriptor': section.descriptor
        }

    def assert_sections_equal(self, a, b):
        self.assertEqual(
            [self.serialize_section(s) for s in a],
            [self.serialize_section(s) for s in b])

    def test_content_section(self):
        workspace1 = self.mk_workspace(name='barefootlaw')
        workspace2 = self.mk_workspace(name='ffl')
        testing.setUp(settings={
            'unicore.repos_dir': self.working_dir,
            'unicore.content_repo_urls': '\n'.join([workspace1.working_dir,
                                                    workspace2.working_dir]),
        })
        views = IoGTViews(self.mk_request())

        self.assertTrue(ContentSection.exists(
            'barefootlaw', views.all_pages.get_indexes()))
        section_obj = ContentSection('ffl')
        self.assertEqual(section_obj.slug, 'ffl')
        self.assertEqual(
            section_obj.set_indexes(views.all_pages).get_indexes(),
            ['ffl-master'])
        self.assertEqual(section_obj.title, 'Facts For Life')
        self.assertEqual(section_obj.owner, 'Facts For Life')
        self.assertEqual(len(ContentSection.all()), len(ContentSection.DATA))
        self.assertEqual(len(ContentSection.known(
            indexes=['ffl', 'ureport', 'does-not-exist'])), 2)
        self.assertEqual(len(ContentSection.known(
            indexes=['ffl', 'barefootlaw', 'does-not-exist'])), 2)

    def test_content_section_translations(self):
        localizer = make_localizer(
            current_locale_name='fre_FR',
            translation_directories=['springboard_iogt/locale']
        )

        sections = ContentSection.known(indexes=['ffl'], localizer=localizer)
        section_obj = sections[0]
        self.assertEqual(section_obj.slug, 'ffl')
        self.assertEqual(section_obj.title, 'Savoir pour Sauver')

    def test_known_indexes(self):
        localizer = make_localizer(
            current_locale_name='fre_FR',
            translation_directories=['springboard_iogt/locale'])

        self.assert_sections_equal(
            ContentSection.known_indexes(['ffl', 'ureport'], localizer),
            [ContentSection('ffl', localizer, 'ffl'),
             ContentSection('ureport', localizer, 'ureport')])

    def test_known_indexes_no_matches(self):
        localizer = make_localizer(
            current_locale_name='fre_FR',
            translation_directories=['springboard_iogt/locale'])

        self.assert_sections_equal(
            ContentSection.known_indexes(['win', 'rar'], localizer),
            [])

    def test_known_indexes_multiple_matches(self):
        localizer = make_localizer(
            current_locale_name='fre_FR',
            translation_directories=['springboard_iogt/locale'])

        self.assert_sections_equal(
            ContentSection.known_indexes(['fflazer', 'fflafel'], localizer),
            [ContentSection('ffl', localizer, 'fflazer'),
             ContentSection('ffl', localizer, 'fflafel')])
