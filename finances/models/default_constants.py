from django.db import models


class Constants(models.Model):
    MIN_ONE_TIME_PAPER_PRICE = 'MIN_ONE_TIME_PAPER_PRICE'
    MIN_TEACHERS_SALARY = 'MIN_TEACHERS_SALARY'
    NAME_CHOICES = [
        (MIN_ONE_TIME_PAPER_PRICE, 'Вартість одного використання мегапапірця'),
        (MIN_TEACHERS_SALARY, 'Мінімальна винагорода за заняття'),
    ]
    name = models.CharField('назва', max_length=100,
                            choices=NAME_CHOICES, unique=True)
    value = models.FloatField('значення', default=0)
    description = models.TextField(
        'додаткова інформація', blank=True)

    @classmethod
    def get_min_teachers_salary(cls):
        return cls.objects.get(name=cls.MIN_TEACHERS_SALARY).value

    @classmethod
    def get_min_one_time_paper_price(cls):
        return cls.objects.get(name=cls.MIN_ONE_TIME_PAPER_PRICE).value

    class Meta:
        verbose_name = 'Стале значення'
        verbose_name_plural = 'Сталі значення'

    def __str__(self):
        return self.name
