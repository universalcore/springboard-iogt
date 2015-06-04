from urlparse import urlparse, parse_qsl, urlunparse
from urllib import urlencode

from pyramid.interfaces import IRoutesMapper
from pyramid.i18n import TranslationStringFactory

from unicore.hub.client.utils import same_origin


translation_string_factory = TranslationStringFactory(None)
_ = translation_string_factory


class ContentSection(object):
    SLUGS = [
        'barefootlaw',
        'ffl',
        'mariestopes',
        'straighttalk',
        'ureport'
    ]
    OWNERS = [
        _('Barefoot Law'),
        _('Facts For Life'),
        _('Marie Stopes'),
        _('Straight Talk'),
        _('U-report'),
    ]
    TITLES = [
        _('Your rights'),
        _('Health advice'),
        _('Youth'),
        _('Sexual health'),
        _('U-report'),
    ]

    def __init__(self, slug, pages, categories, localisations):
        self.slug = slug
        i = self.__class__.SLUGS.index(slug)
        self.owner = self.__class__.OWNERS[i]
        self.title = self.__class__.TITLES[i]
        indexes = pages.get_indexes()
        [self.index] = filter(lambda index: slug in index, indexes)
        self.pages = pages.indexes(self.index)
        self.categories = categories.indexes(self.index)
        self.localisations = localisations.indexes(self.index)

    @classmethod
    def exists(cls, slug, indexes):
        return (slug in cls.SLUGS and
                any([index for index in indexes if slug in index]))


def get_redirect_url(request, param_name='next', default_route='home'):
    redirect_url = request.GET.get(param_name)
    if redirect_url and same_origin(redirect_url, request.current_route_url()):
        return redirect_url
    return request.route_url(default_route)


def get_matching_route(request):
    registry = request.registry
    mapper = registry.queryUtility(IRoutesMapper)
    return mapper(request)['route']


def update_query(url, query_list):
    parts = urlparse(url)
    query = parse_qsl(parts.query)
    query.extend(query_list)
    return urlunparse(parts[:4] + (urlencode(query), ) + parts[5:])
