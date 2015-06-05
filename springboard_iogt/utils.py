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
        _('Ur rights'),
        _('Facts for Life'),
        _('TeenTalk'),
        _('Sex+You'),
        _('U-report'),
    ]

    def __init__(self, slug):
        self.slug = slug
        i = self.__class__.SLUGS.index(slug)
        self.owner = self.__class__.OWNERS[i]
        self.title = self.__class__.TITLES[i]

    def set_indexes(self, s_obj):
        indexes = s_obj.get_indexes()
        indexes = filter(lambda index: self.slug in index, indexes)
        return s_obj.indexes(*indexes)

    @classmethod
    def exists(cls, slug, indexes):
        return (slug in cls.SLUGS and
                any([index for index in indexes if slug in index]))

    @classmethod
    def all(cls):
        return [cls(slug) for slug in cls.SLUGS]


def get_redirect_url(request, param_name='next', default_route='home'):
    redirect_url = request.GET.get(param_name)
    if redirect_url and same_origin(redirect_url, request.current_route_url()):
        return redirect_url
    return request.route_url(default_route)


def get_matching_route(request):
    registry = request.registry
    mapper = registry.queryUtility(IRoutesMapper)
    return mapper(request)['route']
