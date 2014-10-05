from django.core.urlresolvers import reverse
from django.db import models
from django.utils.crypto import get_random_string


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

    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    perk = models.PositiveSmallIntegerField(choices=PERK_CHOICES)
    appearance = models.CharField(max_length=1, choices=APPEARANCE_CHOICES)

    logo = models.URLField(
        max_length=250, blank=True,
        help_text="URL of your logo (silver and above)")
    link = models.URLField(
        max_length=250, blank=True,
        help_text="URL of your website (silver and above)")
    why = models.TextField(
        max_length=250, blank=True,
        help_text="Reason why you support the project (gold and above)")

    token = models.CharField(max_length=12, editable=False)

    def __unicode__(self):
        return '"%s" <%s>' % (self.name, self.email)

    def save(self, *args, **kwargs):
        if self.id is None:
            self.token = get_random_string(length=12)
        super(Funder, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('mtefd-funder-info', kwargs={'token': self.token})
