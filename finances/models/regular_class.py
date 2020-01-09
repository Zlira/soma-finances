from django.db import models


class RegularClass(models.Model):
    name = models.CharField('назва', max_length=260)
    start_date = models.DateField('дата початку')
    end_date = models.DateField('дата кінця', null=True, blank=True)
    one_time_price = models.IntegerField('ціна за одне заняття', blank=True, null=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курси'

    def __str__(self):
        return self.name

