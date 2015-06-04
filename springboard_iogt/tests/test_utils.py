from pyramid import testing

from springboard.tests import SpringboardTestCase

from springboard_iogt.utils import ContentSection
from springboard_iogt.views import IoGTViews


class TestUtils(SpringboardTestCase):

    def tearDown(self):
        testing.tearDown()

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
        section_obj = ContentSection(
            'ffl',
            views.all_pages,
            views.all_categories,
            views.all_localisations)
        self.assertEqual(section_obj.index, 'ffl-master')
        self.assertEqual(section_obj.pages.get_indexes(), ['ffl-master'])
        self.assertEqual(section_obj.title, 'Facts for Life')
        self.assertEqual(section_obj.owner, 'Facts For Life')
