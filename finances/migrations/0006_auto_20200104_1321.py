# Generated by Django 3.0.1 on 2020-01-04 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0005_classparticipation_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='one_time_price',
            field=models.IntegerField(default=0, verbose_name='ціна за одне заняття'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='classparticipation',
            name='class_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finances.ClassUnit', verbose_name='заняття'),
        ),
        migrations.AlterField(
            model_name='classparticipation',
            name='paper_used',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='finances.ParticipantPaper', verbose_name='використаний папірець'),
        ),
        migrations.AlterField(
            model_name='classparticipation',
            name='participant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finances.Participant', verbose_name='учасни_ця'),
        ),
        migrations.AlterField(
            model_name='classunit',
            name='participants',
            field=models.ManyToManyField(through='finances.ClassParticipation', to='finances.Participant', verbose_name='учасни_ці'),
        ),
        migrations.AlterField(
            model_name='classunit',
            name='regular_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finances.RegularClass', verbose_name='курс'),
        ),
        migrations.AlterField(
            model_name='participantpaper',
            name='date_purchased',
            field=models.DateField(verbose_name='дата купівлі'),
        ),
        migrations.AlterField(
            model_name='participantpaper',
            name='expired',
            field=models.BinaryField(verbose_name='недійсний'),
        ),
        migrations.AlterField(
            model_name='participantpaper',
            name='paper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finances.Paper', verbose_name='папірець'),
        ),
        migrations.AlterField(
            model_name='participantpaper',
            name='participant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finances.Participant', verbose_name='учасни_ця'),
        ),
        migrations.AlterField(
            model_name='participantpaper',
            name='price',
            field=models.IntegerField(verbose_name='ціна'),
        ),
        migrations.AlterField(
            model_name='regularclass',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='finances.Teacher', verbose_name='викладач/ка'),
        ),
    ]
