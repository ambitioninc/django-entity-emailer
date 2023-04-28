# -*- coding: utf-8 -*-

from django.db import models, migrations
import django.db.models.deletion
import datetime
import uuid


if hasattr(models, 'UUIDField'):
    uuid_field = ('view_uid', models.UUIDField(default=uuid.uuid4, editable=False))
else:
    import uuidfield.fields
    uuid_field = ('view_uid', uuidfield.fields.UUIDField(editable=False, unique=True, max_length=32, blank=True)),


class Migration(migrations.Migration):

    dependencies = [
        ('entity_event', '0001_initial'),
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                uuid_field,
                ('subject', models.CharField(max_length=256)),
                ('from_address', models.CharField(default='', max_length=256)),
                ('uid', models.CharField(null=True, default=None, unique=True, max_length=100)),
                ('scheduled', models.DateTimeField(null=True, default=datetime.datetime.utcnow)),
                ('sent', models.DateTimeField(null=True, default=None)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entity_event.Event')),
                ('recipients', models.ManyToManyField(to='entity.Entity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
