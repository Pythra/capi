# Generated by Django 3.2 on 2021-04-12 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cap', '0009_plans'),
    ]

    operations = [
        migrations.AddField(
            model_name='plans',
            name='tag',
            field=models.TextField(default=2),
            preserve_default=False,
        ),
    ]
