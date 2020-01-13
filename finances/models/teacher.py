from itertools import groupby
from operator import itemgetter

from django.db import models

import pandas as pd

from .constants import ONE_TIME_PRICE_LABEL, MIN_TEACHERS_SALARY
from .paper import Paper
from .class_unit import ClassUnit


class Teacher(models.Model):
    name = models.CharField("ім'я", max_length=260)

    class Meta:
        verbose_name = 'Викладач_ка'
        verbose_name_plural = 'Викладач_ки'

    def __str__(self):
        return self.name

    def get_classes_for_period(self, start_date, end_date):
        # TODO do i even need this?
        return RegularClass.objects.filter(
            classunit__teacher=self,
            classunit__date__gte=start_date,
            classunit__date__lte=end_date,
        ).distinct()

    def get_detailed_salary_for_period(self, start_date, end_date):
        # TODO subtruct volonteer papers
        # TODO split this to some usable functions
        paper_prices = (
            Paper.objects
            .annotate(one_time_price=Paper.get_one_time_price_expression())
            .values('id', 'one_time_price', 'name')
        )
        paper_prices = {
            str(item['id']): {'name': item['name'], 'price': item['one_time_price']}
            for item in paper_prices
        }
        prices_df = pd.DataFrame.from_dict(paper_prices)
        units = ClassUnit.objects.filter(
            teacher=self,
            date__gte=start_date,
            date__lte=end_date,
        ).order_by('regular_class', 'date').select_related('regular_class')
        unit_payments = []
        for unit in units:
            payment_methods = unit.get_price_by_payement_methods()
            unit_payments.append({
                'regular_class': unit.regular_class, 'date': unit.date,
                'payment_methods':payment_methods,
            })
        res = {}
        for regular_class, unit_group in groupby(unit_payments, itemgetter('regular_class')):
            prices_df = prices_df.assign(**{
                ONE_TIME_PRICE_LABEL: pd.Series(
                    [ONE_TIME_PRICE_LABEL, regular_class.one_time_price],
                    index=['name', 'price']
                )
            })
            salary_df = pd.DataFrame.from_dict(
                {i['date']: i['payment_methods'] for i in unit_group}, orient='index'
            ).fillna(0).astype(int)
            unit_salary = (salary_df * prices_df.loc['price']).sum(axis=1) / 2
            unit_salary = unit_salary.where(
                unit_salary >= MIN_TEACHERS_SALARY, MIN_TEACHERS_SALARY
            )
            salary_df.columns = [prices_df.loc['name', col] for col in salary_df]
            unit_salary_label = 'всього за заняття'
            salary_df = salary_df.assign(**{unit_salary_label: unit_salary})
            res[regular_class.name] = salary_df
        return res

