# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0003_clientapp_reg_lrs_account_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccesstoken_lrs',
            name='clientapp',
            field=models.ForeignKey(default=1, to='xapi.ClientApp'),
            preserve_default=False,
        ),
    ]
