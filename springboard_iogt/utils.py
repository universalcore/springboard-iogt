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
            'owner': _('U-Report'),
            'title': _('U-Report'),
            'descriptor': _('Become a U-Reporter & start sharing!'),
            'name': 'ureport',
            'banner_url': 'springboard_iogt:static/img/ureport_banner.jpg'
        }),
        ('yourrights', {
            'owner': _('Barefoot Law'),
            'title': _('Your Rights'),
            'descriptor': _('Know and use them!'),
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
        ('emergency', {
            'owner': _('Emergency'),
            'title': _('Emergency Information'),
            'descriptor': _('Epidemics, disasters or conflicts'),
            'name': 'ebola'
        }),
        ('ecd', {
            'owner': _('Early Childhood Development'),
            'title': _('Early Life Tips!'),
            'descriptor': _('Care for your Child Development'),
            'name': 'ecd'
        }),
        ('ffl', {
            'owner': _('Facts For Life'),
            'title': _('Facts For Life'),
            'descriptor': _('Improve the lives of Children'),
            'name': 'ffl'
        }),
        ('allin', {
            'owner': _('ALL IN'),
            'title': _('ALL IN'),
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

    def __init__(self, slug, localizer=None, index=None):
        self.slug = slug
        self.data = self.__class__.DATA[slug]
        self.banner_url = self.data.get('banner_url')
        self.index = index
        if localizer:
            self.title = localizer.translate(self.data['title'])
            self.owner = localizer.translate(self.data['owner'])
            self.descriptor = localizer.translate(self.data['descriptor'])
        else:
            self.title = self.data['title']
            self.owner = self.data['owner']
            self.descriptor = self.data['descriptor']

    def set_indexes(self, s_obj):
        indexes = s_obj.get_indexes()
        indexes = filter(lambda index: self.data.get('name') in index, indexes)
        return s_obj.indexes(*indexes)

    @classmethod
    def exists(cls, name, indexes):
        return (
            name in [
                section.get('name') for slug, section in cls.DATA.items()] and
            any(index for index in indexes if name in index))

    @classmethod
    def all(cls):
        return [cls(slug) for slug in cls.DATA.keys()]

    @classmethod
    def known(cls, indexes, localizer=None):
        return [cls(slug, localizer) for slug, section in cls.DATA.items()
                if cls.exists(section.get('name'), indexes)]

    @classmethod
    def known_indexes(cls, indexes, localizer=None):
        sections = (
            cls(slug, localizer, index)
            for slug, section in cls.DATA.iteritems()
            for index in matches(indexes, section['name']))

        return sorted(sections, key=lambda k: k.index)

    @classmethod
    def _for(cls, name, localizer=None):
        [obj] = [
            cls(slug, localizer) for slug, data in cls.DATA.items()
            if data.get('name') == name]
        return obj


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


def matches(strs, substr):
    return (s for s in strs if substr in s)
