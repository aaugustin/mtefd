# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Funder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('perk', models.PositiveSmallIntegerField(choices=[(0, b''), (1, b'Thanks!'), (2, b'Double thanks!'), (3, b'Bronze sponsor'), (4, b'Silver sponsor'), (5, b'Gold sponsor'), (6, b'Platinum sponsor'), (7, b'Diamond sponsor')])),
                ('appearance', models.CharField(max_length=1, choices=[(b'V', b'Visible'), (b'I', b'Identity-Only'), (b'A', b'Anonymous')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
