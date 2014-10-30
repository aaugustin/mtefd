import os.path
import re

from django.core.cache import cache

from docutils.core import publish_parts


def dep_html():
    base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    dep_file = os.path.join(base_dir, 'multiple-template-engines.rst')
    cache_key = 'dep_html_%d' % (int(os.path.getmtime(dep_file)) - 1412100000)

    dep_html = cache.get(cache_key)
    if dep_html is not None:
        return dep_html

    with open(dep_file) as dep_handle:
        dep_rst = dep_handle.read()

    options = {'initial_header_level': 2, 'syntax_highlight': 'short'}
    dep_html = publish_parts(dep_rst, writer_name='html',
                             settings_overrides=options)['html_body']

    table_re = re.compile(r'<table border="1" class="docutils">.*?</table>',
                          re.DOTALL)
    dep_html = table_re.sub('', dep_html, count=1)

    cache.set(cache_key, dep_html, 30 * 86400)
    return dep_html
