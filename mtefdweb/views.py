import os.path
import re

from django.contrib import messages
from django.shortcuts import render
from django.views.generic.edit import UpdateView

from docutils.core import publish_parts

from .models import Funder


def campaign(request):
    return render(request, 'mtefdweb/campaign.html')


def dep(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    dep_file = os.path.join(base_dir, 'multiple-template-engines.rst')
    with open(dep_file) as dep_handle:
        dep_rst = dep_handle.read()

    options = {'initial_header_level': 2}
    dep_html = publish_parts(dep_rst, writer_name='html',
                             settings_overrides=options)['html_body']

    table_re = re.compile(r'<table border="1" class="docutils">.*?</table>',
                          re.DOTALL)
    dep_html = table_re.sub('', dep_html, count=1)

    return render(request, 'mtefdweb/dep.html', {'dep_html': dep_html})


class FunderInfo(UpdateView):
    model = Funder
    fields = ['name', 'email', 'appearance', 'logo', 'link', 'why']
    slug_field = 'token'
    slug_url_kwarg = 'token'

    def form_valid(self, form):
        messages.info(self.request, "Changes saved.")
        return super(FunderInfo, self).form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Please fix errors below.")
        return super(FunderInfo, self).form_invalid(form)