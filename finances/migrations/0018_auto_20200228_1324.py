# Generated by Django 3.0.3 on 2020-02-28 11:24

from django.db import migrations, models
import django.utils.timezone
import finances.models.custom_fields


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0017_auto_20200205_1938'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='рік')),
                ('month', models.IntegerField(choices=[(1, 'січень'), (2, 'лютий'), (3, 'березень'), (4, 'квітень'), (5, 'травень'), (6, 'червень'), (7, 'липень'), (8, 'серпень'), (9, 'вересень'), (10, 'жовтень'), (11, 'листопад'), (12, 'грудень')], verbose_name='місяць')),
                ('total_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='баланс за місяць')),
                ('money_left', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='в наявності')),
                ('report', finances.models.custom_fields.SimpleJsonField(blank=True, null=True, verbose_name='звіт')),
            ],
            options={
                'verbose_name': 'Звіт за місяць',
                'verbose_name_plural': 'Звіти за місяць',
                'ordering': ['-year', '-month'],
            },
        ),
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.CharField(choices=[('main', 'основні'), ('bar', 'бар'), ('space', 'простір'), ('fees', 'гонорари')], max_length=191, verbose_name='категорія'),
        ),
        migrations.AlterField(
            model_name='expense',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='дата'),
        ),
        migrations.AddConstraint(
            model_name='monthlyreport',
            constraint=models.UniqueConstraint(fields=('year', 'month'), name='finances_monthlyreport_year_month_unique_together'),
        ),
    ]