# Generated by Django 2.2.13 on 2021-03-02 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entity_emailer', '0003_email_exception'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='num_tries',
            field=models.IntegerField(default=0),
        ),
    ]