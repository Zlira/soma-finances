from django.contrib import admin

# Register your models here.
from .models import (
    Paper, Teacher, RegularClass, Participant,
    ClassUnit
)


class ParticipantPaperInline(admin.TabularInline):
    model = Participant.papers.through
    extra = 1

    verbose_name = 'Папірець учасни_ці'
    verbose_name_plural = 'Папірці учасни_ці'


class ClassParticipationInline(admin.TabularInline):
    # TODO limit papers use to selected user. is it even possible?
    model = ClassUnit.participants.through
    extra = 1

    verbose_name = 'Відвідування заняття'
    verbose_name_plural = 'Відвідування заняття'


class ParticipantAdmin(admin.ModelAdmin):
    inlines = (ParticipantPaperInline, )
    search_fields = ['name']


class ClassUnitAmdin(admin.ModelAdmin):
    class Media:
        js = ('ParticipantPapers.js', )

    list_display = ('regular_class', 'date')
    list_filter = ('regular_class', )
    inlines = (ClassParticipationInline,)



class RegularClassesAdmin(admin.ModelAdmin):
    fields = ('name', 'start_date', 'end_date', 'teacher')
    list_display = ('name', 'teacher')
    list_filter = ('teacher', )



admin.site.register(Paper)
admin.site.register(Teacher)
admin.site.register(RegularClass, RegularClassesAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(ClassUnit, ClassUnitAmdin)