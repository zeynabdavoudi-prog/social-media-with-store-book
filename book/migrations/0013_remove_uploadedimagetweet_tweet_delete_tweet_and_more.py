# Generated by Django 5.0.3 on 2024-03-25 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0012_alter_uploadedimagetweet_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadedimagetweet',
            name='tweet',
        ),
        migrations.DeleteModel(
            name='Tweet',
        ),
        migrations.DeleteModel(
            name='UploadedImageTweet',
        ),
    ]