from django.db import models


CATEGORY_CHOICES =  [
    ("main", 'основні'),
    ("bar", "бар"),
    ("sapce", "простір"),
    ("fees", "гонорари"),
]


class Expense(models.Model):
    category = models.CharField('категорія', max_length=191, choices=CATEGORY_CHOICES)
    description = models.CharField('опис', max_length=250)
    date = models.DateField('дата')
    amount = models.IntegerField('сума', default=0)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Витрати'
        verbose_name_plural = 'Витрати'

    def __str__(self):
        return f'{self.description} ({self.date})'