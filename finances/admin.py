from django.contrib import admin
from django.shortcuts import get_object_or_404

# Register your models here.
from .models import (
    Paper, Teacher, RegularClass, Participant,
    ClassUnit, Donation, SingleEvent, Expense, Constants,
    MonthlyReport,
)
from .forms import AddParticipantPaperForm, DateRangeForm
from .accounting import get_detailed_teachers_salary_for_period, \
    default_salary_range, get_months_report


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
    fields = ('name', 'days_valid', 'number_of_uses',
              ('price', 'one_time_price'))
    readonly_fields = ('one_time_price', )

    def one_time_price(self, obj):
        return obj.get_one_time_price()
    one_time_price.short_description = 'нараховується за одне заняття'


class TeacherAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/teachers_salary.css', )}
    model = Teacher
    change_form_template = 'admin/teacher/change_form.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        form_data = request.GET
        if not form_data:
            form_data = default_salary_range()._asdict()
        date_range_from = DateRangeForm(form_data)
        if not date_range_from.is_valid():
            pass
            # TODO handle invalid form data (through messages?)
        teacher = get_object_or_404(Teacher, pk=object_id)
        salary = get_detailed_teachers_salary_for_period(
            teacher, **date_range_from.cleaned_data
        )

        extra_context['date_range_form'] = DateRangeForm(form_data)
        extra_context['salary'] = salary
        extra_context['total'] = sum(class_.sum_teachers_share() for class_ in salary)

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )


class ParticipantAdmin(admin.ModelAdmin):
    inlines = (AddParticipantPaperInline, ParticipantPaperInline, )
    search_fields = ['name']
    list_display = ('name', 'date_created', 'email_sent')
    list_editable = ('email_sent',)


class ClassUnitAmdin(admin.ModelAdmin):
    # TODO add number of participants and teachers name to listview
    # TODO add filter by teachers
    class Media:
        js = ('ParticipantPapers.js', )

    list_display = ('regular_class', 'date')
    list_filter = ('regular_class', )
    inlines = (ClassParticipationInline,)


class DonationAdmin(admin.ModelAdmin):
    list_display = ('source', 'amount', 'date')


class SingleEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'admission_sum', 'bar_sum', 'overall_sum')


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'category', 'date', 'amount')
    list_filter = ('category', )


class ConstantsAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'description')
    actions = None


class MonthlyReportAdmin(admin.ModelAdmin):
    readonly_fields = ('year', 'month', 'total_balance', 'money_left', )
    exclude = ('report', )
    change_form_template = 'admin/monthly_report/change_form.html'

    class Media:
        js = ('MonthlyReport.js', )

    def has_add_permission(self, request, obj=None):
        return False

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        if obj.is_latest():
            report = get_months_report(obj.year, obj.month)
            obj.total_balance = (
                report['earnings']['total'] - report['expenses']['total']
            )
            obj.report = report
            previous_report = obj.get_previous()
            if previous_report:
                obj.money_left = previous_report.money_left + obj.total_balance
        return obj


    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     import ipdb; ipdb.set_trace();
    #     return super().change_view(request, object_id, form_url, extra_context)


admin.site.register(ClassUnit, ClassUnitAmdin)
admin.site.register(Paper, PaperAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(RegularClass)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(SingleEvent, SingleEventAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Constants, ConstantsAdmin)
admin.site.register(MonthlyReport, MonthlyReportAdmin)