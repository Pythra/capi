# Generated by Django 3.2 on 2021-04-12 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cap', '0011_auto_20210412_2203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plans',
            name='profile',
            field=models.ManyToManyField(blank=True, null=True, related_name='plans', to='cap.Profile'),
        ),
    ]