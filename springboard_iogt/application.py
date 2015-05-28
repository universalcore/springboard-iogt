from ConfigParser import ConfigParser

from pyramid.config import Configurator

import pkg_resources


def main(global_config, **settings):

    cp = ConfigParser()
    cp.readfp(pkg_resources.resource_stream('springboard', 'defaults.ini'))
    defaults = dict(cp.items('springboard:pyramid'))
    defaults['jinja2.filters'] += (
        '\nrecent_pages = springboard_iogt.filters:recent_pages'
        '\ncategory_dict = springboard_iogt.filters:category_dict')
    defaults.update(settings)

    config = Configurator(settings=defaults)
    config.include('springboard.config')
    config.override_asset(
        to_override='springboard:templates/',
        override_with='springboard_iogt:templates/')
    config.add_static_view(
        'static', 'springboard_iogt:static', cache_max_age=3600)

    return config.make_wsgi_app()
