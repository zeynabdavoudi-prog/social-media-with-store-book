# Generated by Django 5.0.3 on 2024-03-24 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0006_delete_uploadedimagetweet'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedImageTweet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='uploads/')),
            ],
        ),
    ]
