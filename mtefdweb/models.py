import datetime

from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.crypto import get_random_string

from markdown import markdown


class Funder(models.Model):

    APPEARANCE_CHOICES = [
        ('V', "Visible"),
        ('I', "Identity-Only"),
        ('A', "Anonymous"),
    ]
    PERK_CHOICES = list(enumerate([
        '',
        'Thanks!',
        'Double thanks!',
        'Bronze sponsor',
        'Silver sponsor',
        'Gold sponsor',
        'Platinum sponsor',
        'Diamond sponsor',
    ]))

    name = models.CharField(
        max_length=100,
        help_text="Your name appears on the funders page "
                  "unless you set your Appearance to Anonymous.")
    email = models.CharField(
        max_length=100,
        help_text="Your email address is your identifier on this website. "
                  "It will never be displayed or shared with anyone.")

    perk = models.PositiveSmallIntegerField(choices=PERK_CHOICES)
    appearance = models.CharField(
        max_length=1, choices=APPEARANCE_CHOICES,
        help_text="Visible: your name and your contribution are shown. "
                  "Identity-Only: your name is shown in \"special thanks\". "
                  "Anonymous: your contribution is shown as Anonymous.")

    logo = models.URLField(
        max_length=250, blank=True,
        help_text="URL of your logo (silver and above). "
                  "Leave empty if you don't want a logo.")
    link = models.URLField(
        max_length=250, blank=True,
        help_text="URL of your website (silver and above). "
                  "Leave empty if you don't want a link.")
    why = models.TextField(
        max_length=250, blank=True,
        help_text="Reason why you support the project (gold and above). "
                  "Leave empty if you don't want to give a reason.")

    token = models.CharField(max_length=12, editable=False)

    def __unicode__(self):
        return '"%s" <%s>' % (self.name, self.email)

    def save(self, *args, **kwargs):
        if self.id is None:
            self.token = get_random_string(length=12)
        super(Funder, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('mtefd-funder-info', kwargs={'token': self.token})

    @property
    def display_name(self):
        return "Anonymous" if self.appearance == 'A' else self.name

    def send_token(self):
        template = u"""
Hello {name},

Thanks for funding Multiple Template Engines for Django!

Here's the private link to edit your funder profile:
https://myks.org{link}

Best regards,

--
Aymeric.
"""
        send_mail(
            "Your funder profile",
            template.format(name=self.name, link=self.get_absolute_url()),
            "aymeric.augustin@polytechnique.org",
            [self.email])


class Update(models.Model):

    MARKDOWN_OPTIONS = {
        'extensions': ['nl2br', 'sane_lists'],
        'output_format': 'html5',
    }

    title = models.CharField(max_length=100)
    date = models.DateField(default=datetime.date.today, unique=True)

    body = models.TextField(help_text="Markdown syntax")
    html = models.TextField(editable=False)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.date)

    def save(self, *args, **kwargs):
        self.html = markdown(self.body, **self.MARKDOWN_OPTIONS)
        super(Update, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '%s#%s' % (reverse('mtefd-updates'), self.date)
