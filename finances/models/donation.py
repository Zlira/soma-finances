from django.db import models


# TODO if donation is associated with something like the purchase of
# a paper should it be deleted when the ParticipantPapar is deleted?
# probably not but worth a check
class Donation(models.Model):
    date = models.DateField('дата')
    amount = models.IntegerField('сума')
    source = models.TextField('джерело', blank=True, null=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Пожертва'
        verbose_name_plural = 'Пожертви'

    def __str__(self):
        return f'{self.source} ({self.amount} грн)'