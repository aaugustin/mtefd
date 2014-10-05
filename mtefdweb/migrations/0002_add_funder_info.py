# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtefdweb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='funder',
            name='link',
            field=models.URLField(default='', help_text=b'URL of your website (silver and above)', max_length=250, blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='funder',
            name='logo',
            field=models.URLField(default='', help_text=b'URL of your logo (silver and above)', max_length=250, blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='funder',
            name='token',
            field=models.CharField(default='', max_length=12, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='funder',
            name='why',
            field=models.TextField(default='', help_text=b'Reason why you support the project (gold and above)', max_length=250, blank=True),
            preserve_default=False,
        ),
    ]
