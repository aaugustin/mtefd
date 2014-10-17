# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtefdweb', '0004_edit_funder_info_help_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funder',
            name='email',
            field=models.CharField(help_text=b'Your email address is your identifier on this website. It will never be displayed or shared with anyone.', max_length=100),
        ),
        migrations.AlterField(
            model_name='funder',
            name='name',
            field=models.CharField(help_text=b'Your name appears on the funders page unless you set your Appearance to Anonymous.', max_length=100),
        ),
    ]
