# Generated by Django 3.1.6 on 2021-02-07 11:50

import creditcards.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cap', '0003_auto_20210207_1241'),
    ]

    operations = [
        migrations.CreateModel(
            name='Withdraw',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.CharField(blank=True, max_length=36, null=True)),
                ('cc_number', creditcards.models.CardNumberField(max_length=25, verbose_name='card number')),
                ('cc_expiry', creditcards.models.CardExpiryField(verbose_name='expiration date')),
                ('cc_code', creditcards.models.SecurityCodeField(max_length=4, verbose_name='security code')),
            ],
        ),
        migrations.DeleteModel(
            name='Payment',
        ),
    ]
