from ConfigParser import ConfigParser

from pyramid.config import Configurator

import pkg_resources


def main(global_config, **settings):

    cp = ConfigParser()
    cp.readfp(pkg_resources.resource_stream('springboard', 'defaults.ini'))
    defaults = dict(cp.items('springboard:pyramid'))
    defaults['jinja2.filters'] += (
        '\nrecent_pages = springboard_iogt.filters:recent_pages'
        '\ncategory_dict = springboard_iogt.filters:category_dict\n'
        'page_content_section = springboard_iogt.filters:page_content_section')
    defaults.update(settings)

    config = Configurator(settings=defaults)

    # add to springboard routes
    config.add_route('content_section', '/section/{slug}/')
    config.add_route('personae', '/persona/')
    config.add_route('skip_persona_selection', '/persona/skip/')
    config.add_route('select_persona', '/persona/{slug}/')
    config.add_tween('springboard_iogt.views.persona_tween_factory')
    config.scan('.views')
    config.scan('.events')

    config.include('springboard.config')
    config.override_asset(
        to_override='springboard:templates/',
        override_with='springboard_iogt:templates/')
    config.add_static_view(
        'static', 'springboard_iogt:static', cache_max_age=3600)

    return config.make_wsgi_app()
