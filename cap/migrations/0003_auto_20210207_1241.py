# Generated by Django 3.1.6 on 2021-02-07 11:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cap', '0002_auto_20210207_0236'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('crypto', models.CharField(max_length=100)),
                ('created_on', models.TimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crypto', models.CharField(max_length=100)),
                ('total', models.PositiveIntegerField(max_length=100)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Cryptocurrency',
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
    ]