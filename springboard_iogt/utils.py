from collections import OrderedDict
from urlparse import urlparse, parse_qsl, urlunparse
from urllib import urlencode

from pyramid.interfaces import IRoutesMapper
from pyramid.i18n import TranslationStringFactory

from unicore.hub.client.utils import same_origin


translation_string_factory = TranslationStringFactory(None)
_ = translation_string_factory


class ContentSection(object):
    DATA = OrderedDict([
        ('ureport', {
            'owner': _('U-report'),
            'title': _('U-report'),
            'descriptor': _('Become a U-Reporter & start sharing!'),
            'name': 'ureport'
        }),
        ('yourrights', {
            'owner': _('Barefoot Law'),
            'title': _('Your Rights'),
            'descriptor': _('Free legal information & support'),
            'name': 'barefootlaw'
        }),
        ('myfamily', {
            'owner': _('Marie Stopes'),
            'title': _('My Family'),
            'descriptor': _('Matters about the family'),
            'name': 'mariestopes'
        }),
        ('healthtalk', {
            'owner': _('Straight Talk'),
            'title': _('Health Talk'),
            'descriptor': _('Collaborating together with the youth'),
            'name': 'straighttalk'
        }),
        ('ebola', {
            'owner': _('Ebola Response'),
            'title': _('StopEbola'),
            'descriptor': _('Get information about Ebola'),
            'name': 'ebola'
        }),
        ('ffl', {
            'owner': _('Facts For Life'),
            'title': _('Facts for Life'),
            'descriptor': _('Improve the lives of Children'),
            'name': 'ffl'
        }),
        ('hiv', {
            'owner': _('HIV'),
            'title': _('HIV'),
            'descriptor': _('Love, relationships, sex and gender'),
            'name': 'hiv'
        }),
        ('connectsmart', {
            'owner': _('Connect Smart'),
            'title': _('Connect Smart'),
            'descriptor': _('Learn about the internet'),
            'name': 'connectsmart'
        })
    ])

    def __init__(self, slug):
        self.slug = slug
        [self.data] = [
            data for _, data in self.__class__.DATA.items()
            if data.get('name') == slug]
        self.owner = self.data['owner']
        self.title = self.data['title']
        self.descriptor = self.data['descriptor']

    def set_indexes(self, s_obj):
        indexes = s_obj.get_indexes()
        indexes = filter(lambda index: self.slug in index, indexes)
        return s_obj.indexes(*indexes)

    @classmethod
    def exists(cls, name, indexes):
        return (
            name in [
                section.get('name') for _section, section in cls.DATA.items()]
            and
            any(index for index in indexes if name in index))

    @classmethod
    def all(cls):
        return [cls(section.get('name')) for slug, section in cls.DATA.items()]

    @classmethod
    def known(cls, indexes):
        return [cls(section.get('name')) for slug, section in cls.DATA.items()
                if cls.exists(section.get('name'), indexes)]


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
