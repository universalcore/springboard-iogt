from random import randint, shuffle

from pyramid.view import view_config
from beaker.cache import cache_region
from elasticutils import F

from springboard.views.base import SpringboardViews


HOUR_CACHE_REGION = 'hour'


class IoGTViews(SpringboardViews):

    @view_config(route_name='home',
                 renderer='springboard_iogt:templates/home.jinja2')
    def index_view(self):
        content = self.recent_content(self.language, 8)
        content = [(c.to_object(), p.to_object()) for c, p in content]
        return self.context(recent_content=content)

    @cache_region(HOUR_CACHE_REGION)
    def recent_content(self, language, limit):
        categories = self.all_categories.filter(
            language=language).everything()

        def get_category_object(uuid):
            if not uuid:
                return None
            [category] = filter(lambda c: c.uuid == uuid, categories)
            return category

        # get 2 most recent pages
        [page1, page2] = self.all_pages.filter(
            language=self.language).order_by('-created_at')[:2]
        category1 = get_category_object(page1.primary_category)
        category2 = get_category_object(page2.primary_category)

        # get most recent page per category
        # exclude the 2 most recent overall
        content = []
        f = ~F(uuid=page1.uuid) & ~F(uuid=page2.uuid)
        for category in categories:
            try:
                f_cat = F(primary_category=category.uuid)
                [page] = self.all_pages.filter(f & f_cat).order_by(
                    '-created_at')[:1]
                content.append((category, page))
            except ValueError:
                pass

        shuffle(content)
        content = content[:limit - 2]
        content.insert(randint(0, len(content)), (category1, page1))
        content.insert(randint(0, len(content)), (category2, page2))
        return content
