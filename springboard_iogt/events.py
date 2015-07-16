from pyramid.events import BeforeRender, subscriber

from springboard_iogt.utils import ContentSection


@subscriber(BeforeRender)
def add_content_section_context(event):
    index_prefixes = getattr(event.get('view'), 'all_index_prefixes', None)
    event['content_sections'] = (ContentSection.active(index_prefixes)
                                 if index_prefixes
                                 else [])
