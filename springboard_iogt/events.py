from pyramid.events import BeforeRender, subscriber

from springboard_iogt.utils import ContentSection


@subscriber(BeforeRender)
def add_content_section_context(event):
    event['content_sections'] = ContentSection.all()
