from django.contrib import admin

import pandas as pd

# Register your models here.
from .models import (
    Paper, Teacher, RegularClass, Participant,
    ClassUnit
)
from .forms import AddParticipantPaperForm


class AddParticipantPaperInline(admin.StackedInline):
    model = Participant.papers.through
    form = AddParticipantPaperForm
    fieldsets = [(
        None, {
            'fields': ('paper', 'date_purchased', 'is_volunteer', 'price'),
            'classes': ('add-participant-paper', ),
        }
    )]
    extra = 1
    max_num = 1
    # TODO add the ability to set price (defualt + donation)
    class Media:
        js = ('AddParticipantPaper.js', )

    verbose_name = 'Додати папірець учасни_ці'
    verbose_name_plural = 'Додати папірці учасни_ці'

    def get_queryset(self, obj=None):
        return self.model.objects.none()

    def has_delete_permission(self, request, obj=None):
        return False


class ParticipantPaperInline(admin.TabularInline):
    model = Participant.papers.through
    fields = ('paper', 'is_expired', 'date_purchased', 'is_volunteer',
              'number_of_uses', )
    readonly_fields = ('number_of_uses', 'is_expired', )
    extra = 0
    # TODO add the ability to set price (defualt + donation)

    verbose_name = 'Папірець учасни_ці'
    verbose_name_plural = 'Папірці учасни_ці'

    def has_add_permission(self, request, obj=None):
        return False

    def number_of_uses(self, obj):
        return obj.get_number_of_uses()
    number_of_uses.short_description = 'разів використаний'

    def is_expired(self, obj):
        return 'так' if obj.is_expired() else 'ні'
    is_expired.short_description = 'недійсний'


class ClassParticipationInline(admin.TabularInline):
    # TODO limit papers use to selected user. is it even possible?
    model = ClassUnit.participants.through
    autocomplete_fields = ('participant', )
    extra = 1

    verbose_name = 'Відвідування заняття'
    verbose_name_plural = 'Відвідування заняття'


class PaperAdmin(admin.ModelAdmin):
    model = Teacher
    fields = ('name', 'days_valid', 'number_of_uses', ('price', 'one_time_price'))
    readonly_fields = ('one_time_price', )

    def one_time_price(self, obj):
        return obj.get_one_time_price()
    one_time_price.short_description = 'нараховується за одне заняття'


class TeacherAdmin(admin.ModelAdmin):
    model = Teacher
    change_form_template = 'admin/teacher/change_form.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        teacher = Teacher.objects.get(id=object_id)
        salary_details = teacher.get_detailed_salary_for_period(
            '2019-12-01', '2019-12-15'
        )
        unit_salary_label = 'всього за заняття'
        salary_details = {
            f'{class_name}: {df[unit_salary_label].sum()} грн': df.to_html()
            for class_name, df in salary_details.items()
        }
        extra_context['salary_details'] = salary_details
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )


class ParticipantAdmin(admin.ModelAdmin):
    inlines = (AddParticipantPaperInline, ParticipantPaperInline, )
    search_fields = ['name']


class ClassUnitAmdin(admin.ModelAdmin):
    # TODO add number of participants and teachers name to listview
    # TODO add filter by teachers
    class Media:
        js = ('ParticipantPapers.js', )

    list_display = ('regular_class', 'date')
    list_filter = ('regular_class', )
    inlines = (ClassParticipationInline,)


admin.site.register(ClassUnit, ClassUnitAmdin)
admin.site.register(Paper, PaperAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(RegularClass)
admin.site.register(Participant, ParticipantAdmin)