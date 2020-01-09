from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

from .paper import Paper


class Participant(models.Model):
    # TODO distingiush between several people with the same name
    name = models.CharField("ім'я", max_length=260)
    papers = models.ManyToManyField(Paper, through='ParticipantPaper')
    date_created = models.DateField('дата першого знаяття', auto_now=True)
    phone_number = PhoneNumberField(verbose_name='номер телефону', region="UA", blank=True, null=True)
    email = models.EmailField('електронна адреса', blank=True, null=True)
    # TODO how did you learn about us

    class Meta:
        verbose_name = 'Учасни_ця'
        verbose_name_plural = 'Учасни_ці'

    def __str__(self):
        return self.name

