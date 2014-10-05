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

    def __unicode__(self):
        return '"%s" <%s>' % (self.name, self.email)
