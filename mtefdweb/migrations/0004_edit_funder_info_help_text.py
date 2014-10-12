# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtefdweb', '0003_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funder',
            name='appearance',
            field=models.CharField(help_text=b'Visible: your name and your contribution are shown. Identity-Only: your name is shown in "special thanks". Anonymous: your contribution is shown as Anonymous.', max_length=1, choices=[(b'V', b'Visible'), (b'I', b'Identity-Only'), (b'A', b'Anonymous')]),
        ),
        migrations.AlterField(
            model_name='funder',
            name='link',
            field=models.URLField(help_text=b"URL of your website (silver and above). Leave empty if you don't want a link.", max_length=250, blank=True),
        ),
        migrations.AlterField(
            model_name='funder',
            name='logo',
            field=models.URLField(help_text=b"URL of your logo (silver and above). Leave empty if you don't want a logo.", max_length=250, blank=True),
        ),
        migrations.AlterField(
            model_name='funder',
            name='why',
            field=models.TextField(help_text=b"Reason why you support the project (gold and above). Leave empty if you don't want to give a reason.", max_length=250, blank=True),
        ),
    ]
