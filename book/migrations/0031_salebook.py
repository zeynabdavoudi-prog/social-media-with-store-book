# Generated by Django 5.0.3 on 2024-05-23 08:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0030_relation_show'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SaleBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_book', models.CharField()),
                ('price', models.IntegerField()),
                ('author', models.CharField()),
                ('print_year', models.DateTimeField()),
                ('period_print', models.DateTimeField()),
                ('number_of_page', models.IntegerField()),
                ('photo', models.ImageField(upload_to='photosalebook/')),
                ('category', models.CharField()),
                ('book_introduction', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usbook', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]