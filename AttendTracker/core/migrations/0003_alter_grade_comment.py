# Generated by Django 5.2 on 2025-05-05 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_grade_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
