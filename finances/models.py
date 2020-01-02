from django.db import models

# TODO add unique constraints

class Paper(models.Model):
    paper_type = models.CharField('тип', max_length=260)
    min_price = models.IntegerField('мінімальна ціна')
    max_price = models.IntegerField('максимальна ціна')
    # days_valid = models.IntegerField('скільки днів дійсний', null=True)
    # todo maybe number of times used
    # description

    class Meta:
        verbose_name = 'Папірець'
        verbose_name_plural = 'Папірці'

    def __str__(self):
        return self.paper_type



class Teacher(models.Model):
    name = models.CharField("ім'я", max_length=260)

    class Meta:
        verbose_name = 'Викладач_ка'
        verbose_name_plural = 'Викладач_ки'

    def __str__(self):
        return self.name


class RegularClass(models.Model):
    name = models.CharField('назва', max_length=260)
    start_date = models.DateField('дата початку')
    end_date = models.DateField('дата кінця', null=True, blank=True)
    teacher = models.ForeignKey(
        Teacher, blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name='викладач/ка',
    )
    # schedule
    # one time price

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курси'

    def __str__(self):
        return self.name


class Participant(models.Model):
    # todo distingiush between several people with the same name
    name = models.CharField("ім'я", max_length=260)
    papers = models.ManyToManyField(Paper, through='ParticipantPaper')
    # mail, phone number etc

    class Meta:
        verbose_name = 'Учасни_ця'
        verbose_name_plural = 'Учасни_ці'

    def __str__(self):
        return self.name


class ParticipantPaper(models.Model):
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, verbose_name="учасни_ця",
    )
    paper = models.ForeignKey(
        Paper, on_delete=models.CASCADE, verbose_name="папірець"
    )
    date_purchased = models.DateField("дата купівлі")
    # check with the price of paper
    price = models.IntegerField("ціна")
    expired = models.BinaryField("недійсний")

    def __str__(self):
        # TODO does this issue new db query? should select_releted be used?
        return f"{self.paper.paper_type} належить {self.participant.name}"



class ClassUnit(models.Model):
    regular_class = models.ForeignKey(
        RegularClass, on_delete=models.CASCADE, verbose_name="курс"
    )
    date = models.DateField('дата')
    participants = models.ManyToManyField(
        Participant, through='ClassParticipation', verbose_name="учасни_ці"
    )
    # substitute teacher

    class Meta:
        ordering = ['-date', 'regular_class']
        verbose_name = 'Конкретне заняття'
        verbose_name_plural = 'Конкретні заняття'


    def __str__(self):
        return f'{self.regular_class} ({self.date})'


class ClassParticipation(models.Model):
    class_unit = models.ForeignKey(
        ClassUnit, on_delete=models.CASCADE, verbose_name="заняття"
    )
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, verbose_name="учасни_ця"
    )
    # TODO add restriction that this should be participant's paper, make this field optional
    paper_used = models.ForeignKey(
        ParticipantPaper, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name="використаний папірець"
    )
    one_time_price = models.IntegerField('одноразова ціна', blank=True, null=True)
    comment = models.TextField('коментар', null=True, blank=True)
    # todo volunteer status?

    def __str__(self):
        return f'{self.participant} на {self.class_unit}'