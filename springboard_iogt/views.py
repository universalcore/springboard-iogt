from datetime import datetime
from itertools import chain

from pyramid.view import view_config
from elasticutils import F

from springboard.views.base import SpringboardViews

from springboard_iogt.utils import randomize_query


class IoGTViews(SpringboardViews):

    @view_config(route_name='home',
                 renderer='springboard_iogt:templates/home.jinja2')
    def index_view(self):
        return self.context(recent_content=self.recent_content())

    def recent_content(self):
        # get 2 most recent pages
        [page1, page2] = self.all_pages.filter(
            language=self.language).order_by('-created_at')[:2]
        [category1] = (self.all_categories.filter(uuid=page1.primary_category)
                       if page1.primary_category
                       else None)
        [category2] = (self.all_categories.filter(uuid=page2.primary_category)
                       if page2.primary_category
                       else None)
        most_recent = [(category1, page1), (category2, page2)]

        # random seed that changes hourly
        seed = datetime.utcnow().replace(
            minute=0, second=0, microsecond=0)
        seed = (seed - datetime.utcfromtimestamp(0)).total_seconds()
        seed = int(seed)

        # get most recent page per category
        # exclude the 2 most recent overall
        f = ~F(uuid=page1.uuid) & ~F(uuid=page2.uuid)
        categories = self.all_categories.filter(
            f, language=self.language)
        categories = randomize_query(categories, seed=seed)

        def do_query(limit):
            most_recent_per_category = []
            for category in categories[:limit - 2]:
                [page] = self.all_pages.filter(
                    f, primary_category=category.uuid).order_by(
                    '-created_at')[:1]
                most_recent_per_category.append((category, page))

            return [(c.to_object(), p.to_object()) for c, p
                    in chain(most_recent, most_recent_per_category)]

        return do_query
