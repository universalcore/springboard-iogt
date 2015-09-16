import json
import pkg_resources

from pyramid.view import view_config
from pyramid.events import NewRequest
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from unicore.content.models import Page

from springboard.views.base import SpringboardViews

from springboard.utils import ga_context
from springboard_iogt.utils import (
    get_redirect_url, get_matching_route, update_query, ContentSection)


ONE_YEAR = 31536000

PERSONAE = {'CHILD', 'ADOLESCENT', 'PARENT', 'WORKER'}
PERSONA_COOKIE_NAME = 'iogt-persona'
PERSONA_SKIP_COOKIE_VALUE = '__skip__'
PERSONA_REDIRECT_ROUTES = {'home', 'page', 'category', 'flat_page'}


def persona_tween_factory(handler, registry):

    def persona_tween(request):
        if PERSONA_COOKIE_NAME in request.cookies:
            response = handler(request)

            if request.google_analytics:
                persona = request.cookies[PERSONA_COOKIE_NAME]
                request.google_analytics['path'] = update_query(
                    request.google_analytics.get('path', request.path),
                    [('persona', persona)])

            return response

        route = get_matching_route(request)
        if route and route.name in PERSONA_REDIRECT_ROUTES:
            query = {'next': request.url}
            # Fire NewRequest event here because it won't
            # happen unless we call handler.
            # NOTE: A NewResponse event will be fired.
            request.registry.notify(NewRequest(request=request))
            return HTTPFound(request.route_url('personae', _query=query))

        return handler(request)

    return persona_tween


class IoGTViews(SpringboardViews):

    @ga_context(lambda context: {'dt': 'Choose Persona', })
    @view_config(route_name='personae',
                 renderer='springboard_iogt:templates/personae.jinja2')
    def personae(self):
        return self.context()

    @ga_context(lambda context: {'dt': 'Selected Persona', })
    @view_config(route_name='select_persona')
    def select_persona(self):
        slug = self.request.matchdict['slug'].upper()
        if slug not in PERSONAE:
            raise HTTPNotFound

        # set cookie and redirect
        response = HTTPFound(location=get_redirect_url(self.request))
        response.set_cookie(PERSONA_COOKIE_NAME, value=slug, max_age=ONE_YEAR)

        # set persona dimension value on GA
        # NOTE: the persona dimension has to be configured with scope 'user'
        persona_dimension_id = self.settings.get('ga.persona_dimension_id')
        if persona_dimension_id:
            self.request.google_analytics[persona_dimension_id] = slug

        return response

    @ga_context(lambda context: {'dt': 'Skip Persona Selection', })
    @view_config(route_name='skip_persona_selection')
    def skip_persona_selection(self):
        # set cookie and redirect
        response = HTTPFound(location=get_redirect_url(self.request))
        response.set_cookie(
            PERSONA_COOKIE_NAME, value=PERSONA_SKIP_COOKIE_VALUE,
            max_age=ONE_YEAR)
        return response

    @ga_context(lambda context: {'dt': context['section'].title, })
    @view_config(route_name='content_section',
                 renderer='springboard_iogt:templates/content_section.jinja2')
    def content_section(self):
        slug = self.request.matchdict['slug']

        try:
            section = ContentSection(slug)
        except KeyError:
            raise HTTPNotFound

        return self.context(section=section)

    @ga_context(lambda context: {'dt': 'About', })
    @view_config(route_name='about',
                 renderer='springboard_iogt:templates/flat_page.jinja2')
    def about(self):
        filename = pkg_resources.resource_filename(
            'springboard_iogt',
            'static/other/about-%s.json' % (self.language, ))

        try:
            with open(filename) as f:
                page = Page(json.load(f))
            return self.context(page=page)
        except IOError:
            raise HTTPNotFound
