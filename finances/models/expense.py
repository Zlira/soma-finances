from django.db import models


class Expense(models.Model):
    MAIN_CAT = 'main'
    BAR_CAT = 'bar'
    SPACE_CAT = 'space'
    FEES_CAT = 'fees'
    CATEGORY_CHOICES =  [
        (MAIN_CAT, 'основні'),
        (BAR_CAT, "бар"),
        (SPACE_CAT, "простір"),
        (FEES_CAT, "гонорари"),
    ]

    category = models.CharField('категорія', max_length=191, choices=CATEGORY_CHOICES)
    description = models.CharField('опис', max_length=250)
    date = models.DateField('дата', auto_now=True)
    amount = models.IntegerField('сума', default=0)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Витрати'
        verbose_name_plural = 'Витрати'

    def __str__(self):
        return f'{self.description} ({self.date})'