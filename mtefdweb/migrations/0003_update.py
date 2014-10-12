# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('mtefdweb', '0002_add_funder_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('date', models.DateField(default=datetime.date.today, unique=True)),
                ('body', models.TextField(help_text=b'Markdown syntax')),
                ('html', models.TextField(editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
