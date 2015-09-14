from pyramid.events import BeforeRender, subscriber
from springboard.utils import config_dict
from springboard_iogt.utils import ContentSection


@subscriber(BeforeRender)
def add_content_section_context(event):
    index_prefixes = getattr(event.get('view'), 'all_index_prefixes', None)
    event['content_sections'] = (ContentSection.known(index_prefixes)
                                 if index_prefixes
                                 else [])
    settings = event['request'].registry.settings
    overrides = config_dict(
        settings.get('iogt.content_section_url_overrides', ''))
    event['content_section_url_overrides'] = overrides
    event['content_section_url_overrides_data_list'] = [
        {'url': url, 'slug': slug, 'data': ContentSection(slug)}
        for slug, url in overrides.items()]
