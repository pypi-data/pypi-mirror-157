# Generated by Django 3.2.9 on 2021-11-30 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paweljong', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='website',
            field=models.CharField(default='', max_length=255, verbose_name='Website of event'),
            preserve_default=False,
        ),
    ]
