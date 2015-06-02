from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from springboard.views.base import SpringboardViews

from springboard_iogt.utils import (
    get_redirect_url, get_matching_route, ContentSection)


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

    @view_config(route_name='content_section',
                 renderer='springboard_iogt:templates/content_section.jinja2')
    def content_section(self):
        slug = self.request.matchdict['slug']
        indexes = self.all_pages.get_indexes()
        if not ContentSection.exists(slug, indexes):
            raise HTTPNotFound

        return self.context(section=ContentSection(slug, indexes))
