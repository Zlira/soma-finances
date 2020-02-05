# Generated by Django 3.0.1 on 2020-02-05 13:35

from django.db import migrations


def fill_constants(apps, schema_editor):
    Constants = apps.get_model('finances', 'Constants')
    Constants.objects.bulk_create([
        Constants(name='MIN_ONE_TIME_PAPER_PRICE', value=70),
        Constants(name='MIN_TEACHERS_SALARY', value=100)
    ])


def reverse_fill_constants(apps, schema_editor):
    Constants = apps.get_model('finances', 'Constants')
    db_alias = schema_editor.connection.alias
    Constants.objects.using(db_alias).filter(
        name='MIN_ONE_TIME_PAPER_PRICE', value=70).delete()
    Constants.objects.using(db_alias).filter(
        name='MIN_TEACHERS_SALARY', value=100).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0015_auto_20200205_1512'),
    ]

    operations = [
        migrations.RunPython(fill_constants, reverse_fill_constants),
    ]
