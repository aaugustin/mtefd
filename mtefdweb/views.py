import os.path
import re

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.dates import ArchiveIndexView
from django.views.generic.edit import FormView, UpdateView

from docutils.core import publish_parts

from .forms import FunderEmail
from .models import Funder, Update


def campaign(request):
    return render(request, 'mtefdweb/campaign.html')


def dep(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    dep_file = os.path.join(base_dir, 'multiple-template-engines.rst')
    with open(dep_file) as dep_handle:
        dep_rst = dep_handle.read()

    options = {'initial_header_level': 2, 'syntax_highlight': 'short'}
    dep_html = publish_parts(dep_rst, writer_name='html',
                             settings_overrides=options)['html_body']

    table_re = re.compile(r'<table border="1" class="docutils">.*?</table>',
                          re.DOTALL)
    dep_html = table_re.sub('', dep_html, count=1)

    return render(request, 'mtefdweb/dep.html', {'dep_html': dep_html})


def funders(request):
    funders = Funder.objects.order_by('-perk', '?')
    return render(request, 'mtefdweb/funders.html', {
        'sponsors': funders.exclude(appearance='I').filter(perk__gte=3),
        'funders2': funders.exclude(appearance='I').filter(perk=2),
        'funders1': funders.exclude(appearance='I').filter(perk=1),
        'fundersx': funders.filter(appearance='I', perk__gte=1),
    })


class FunderGetToken(FormView):
    form_class = FunderEmail
    success_url = reverse_lazy('mtefd-funder-get-token-done')
    template_name = 'mtefdweb/funder_email.html'

    def form_valid(self, form):
        try:
            funder = Funder.objects.get(email=form.cleaned_data['email'])
        except Funder.DoesNotExist:
            pass                                # don't leak email addresses
        else:
            funder.send_token()
        return super(FunderGetToken, self).form_valid(form)


class FunderGetTokenDone(TemplateView):
    template_name = 'mtefdweb/funder_email_sent.html'


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


class Updates(ArchiveIndexView):
    model = Update
    allow_empty = True
    date_field = 'date'
