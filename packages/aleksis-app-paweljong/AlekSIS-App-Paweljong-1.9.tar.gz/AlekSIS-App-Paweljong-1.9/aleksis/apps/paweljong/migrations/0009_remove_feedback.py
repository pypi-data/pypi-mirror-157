# Generated by Django 3.2.12 on 2022-02-20 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paweljong', '0008_remove_terms_from_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedbackaspect',
            name='site',
        ),
        migrations.RemoveField(
            model_name='event',
            name='feedback_aspects',
        ),
        migrations.DeleteModel(
            name='EventFeedback',
        ),
        migrations.DeleteModel(
            name='FeedbackAspect',
        ),
    ]
