import random
from datetime import datetime
from itertools import chain

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from elasticutils import F

from springboard.views.base import SpringboardViews

from springboard_iogt.utils import (
    randomize_query, get_redirect_url, get_matching_route)


ONE_YEAR = 31536000

PERSONAE = {'CHILD', 'TEENAGER', 'PARENT', 'WORKER'}
PERSONA_COOKIE_NAME = 'iogt-persona'
PERSONA_SKIP_COOKIE_VALUE = '__skip__'
PERSONA_REDIRECT_ROUTES = {'home', 'page', 'category', 'flat_page'}


def persona_tween_factory(handler, registry):

    def persona_tween(request):
        if PERSONA_COOKIE_NAME in request.cookies:
            return handler(request)

        route = get_matching_route(request)
        if route and route.name in PERSONA_REDIRECT_ROUTES:
            query = {'next': request.url}
            return HTTPFound(request.route_url('personae', _query=query))

        return handler(request)

    return persona_tween


class IoGTViews(SpringboardViews):

    @view_config(route_name='home',
                 renderer='springboard_iogt:templates/home.jinja2')
    def index_view(self):
        return self.context(recent_content=self.recent_content())

    def recent_content(self):
        # get 2 most recent pages and their categories
        [page1, page2] = self.all_pages.filter(
            language=self.language).order_by('-created_at')[:2]
        categories = self.all_categories.filter(
            uuid__in=filter(
                None, [page1.primary_category, page2.primary_category]))
        categories = dict((category.uuid, category) for category in categories)
        category1 = categories.get(page1.primary_category)
        category2 = categories.get(page2.primary_category)

        # random seed that changes hourly
        seed = datetime.utcnow().hour

        # get random categories and exclude categories of 2 most recent pages
        categories = self.all_categories.filter(
            ~F(uuid__in=categories.keys()), language=self.language)
        categories = randomize_query(categories, seed=seed)
        # filter to exclude the 2 most recent pages
        f_exclude_pages = ~F(uuid__in=[page1.uuid, page2.uuid])

        def do_query(limit):
            most_recent = [(category1, page1), (category2, page2)]
            most_recent_per_category = []
            # NOTE: this is bad if limit is large
            # We are fetching pages individually, because we
            # can't use facets or aggregates.
            for category in categories[:limit - 2]:
                try:
                    [page] = self.all_pages.filter(
                        f_exclude_pages,
                        primary_category=category.uuid).order_by(
                        '-created_at')[:1]
                    most_recent_per_category.append((category, page))
                except ValueError:
                    pass

            results = [(c.to_object() if c else None, p.to_object())
                       for c, p
                       in chain(most_recent, most_recent_per_category)]
            # randomize position of most_recent content
            random.seed(seed)
            random.shuffle(results)
            return results

        return do_query

    @view_config(route_name='personae',
                 renderer='springboard_iogt:templates/personae.jinja2')
    def personae(self):
        return self.context()

    @view_config(route_name='select_persona')
    def select_persona(self):
        slug = self.request.matchdict['slug'].upper()
        if slug not in PERSONAE:
            raise HTTPNotFound

        # set cookie and redirect
        response = HTTPFound(location=get_redirect_url(self.request))
        response.set_cookie(PERSONA_COOKIE_NAME, value=slug, max_age=ONE_YEAR)
        return response

    @view_config(route_name='skip_persona_selection')
    def skip_persona_selection(self):
        # set cookie and redirect
        response = HTTPFound(location=get_redirect_url(self.request))
        response.set_cookie(
            PERSONA_COOKIE_NAME, value=PERSONA_SKIP_COOKIE_VALUE,
            max_age=ONE_YEAR)
        return response
