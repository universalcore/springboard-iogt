from pyramid.interfaces import IRoutesMapper

from unicore.hub.client.utils import same_origin


def get_redirect_url(request, param_name='next', default_route='home'):
    redirect_url = request.GET.get(param_name)
    if redirect_url and same_origin(redirect_url, request.current_route_url()):
        return redirect_url
    return request.route_url(default_route)


def get_matching_route(request):
    registry = request.registry
    mapper = registry.queryUtility(IRoutesMapper)
    return mapper(request)['route']
