from pyramid.events import BeforeRender, subscriber

from springboard.utils import config_dict

from springboard_iogt.utils import ContentSection


@subscriber(BeforeRender)
def add_content_section_context(event):
    event['content_sections'] = ContentSection.all()
    settings = event['request'].registry.settings
    event['content_section_url_overrides'] = config_dict(
        settings.get('iogt.content_section_url_overrides', ''))
