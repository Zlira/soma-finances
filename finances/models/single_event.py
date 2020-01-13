from django.db import models


class SingleEvent(models.Model):
    name = models.CharField("назва", max_length=191)
    date = models.DateField('дата')
    admission_sum = models.IntegerField('сума внесків', default=0)
    bar_sum = models.IntegerField('сума за бар', default=0)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Одноразова подія'
        verbose_name_plural = 'Одноразові події'

    def __str__(self):
        return f'{self.name} ({self.date})'