import random
from itertools import chain
from datetime import datetime

from elasticutils import F


def recent_pages(s_pages, language):
    s_pages = s_pages.filter(
        language=language, featured=True).order_by('-created_at')
    # get 2 most recent pages
    most_recent = list(s_pages[:2])
    # add most recent page per index, excluding 2 most recent
    s_pages = s_pages.filter(
        ~F(uuid__in=[page.uuid for page in most_recent]))
    most_recent.extend(chain(
        *[s_pages.indexes(index)[:1] for index in s_pages.get_indexes()]))

    # random seed that changes hourly
    seed = datetime.utcnow().hour
    random.seed(seed)
    random.shuffle(most_recent)
    print most_recent
    return [page.to_object() for page in most_recent]


def category_dict(s_categories, uuids):
    categories = s_categories.filter(uuid__in=filter(None, uuids))
    return dict((category.uuid, category.to_object())
                for category in categories)
