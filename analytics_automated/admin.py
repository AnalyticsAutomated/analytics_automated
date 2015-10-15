import re
from django.contrib import admin
from django.core.urlresolvers import reverse

from .models import Backend, Job, Task, Step, Parameter, Result, Validator
from .models import Submission, BackendUser, Message
from .forms import *


class ParameterInline(admin.TabularInline):
    model = Parameter
    extra = 3


class ValidatorInline(admin.TabularInline):
    model = Validator
    formset = ValidatorForm
    extra = 1


class StepInline(admin.TabularInline):
    model = Step
    extra = 3


class BackendUserInline(admin.TabularInline):
    model = BackendUser
    extra = 2


class BackendAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('Configuration', {'fields': ['server_type', 'ip', 'port']}),
        ('Path', {'fields': ['root_path']}),
    ]
    list_display = ('name', 'server_type', 'ip', 'port', 'root_path')
    inlines = [BackendUserInline]


class TaskAdmin(admin.ModelAdmin):
    def processing_backend(self, obj):
        url = reverse('admin:analytics_automated_backend_change',
                      args=(obj.backend.pk,))
        return '<a href="%s">%s</a>' % (url, obj.backend)
    processing_backend.allow_tags = True

    fieldsets = [
        (None,               {'fields': ['name']}),
        ('Details', {'fields': ['backend', 'name', 'in_glob', 'out_glob',
                                'executable']}),
    ]
    inlines = [ParameterInline]
    list_display = ('name', 'processing_backend', 'executable')


class JobAdmin(admin.ModelAdmin):
    inlines = [ValidatorInline, StepInline]
    list_display = ('name', 'runnable', 'number_of_tasks', 'task_list')

    def clean(self):
        start_date = self.cleaned_data.get('start_date')

    def number_of_tasks(self, obj):
        j = Job.objects.get(pk=obj.pk)
        return '%d' % j.steps.count()

    def task_list(self, obj):
        j = Job.objects.get(pk=obj.pk)
        task_list = ""
        for s in j.steps.all():
            url = reverse('admin:analytics_automated_task_change',
                          args=(s.task.pk,))
            task_list += '<a href="%s"> %s </a> ->' % (url, s.task)
        task_list = task_list.rstrip(' ->')
        return task_list
    task_list.allow_tags = True


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'job', 'submission_name', 'email', 'UUID', 'ip',
                    'status', 'claimed', 'message_link', 'step_id', 'created',
                    'modified')

    def message_link(self, obj):
        url = reverse('admin:analytics_automated_message_change',
                      args=(obj.pk,))
        return('<a href="%s">%s</a>' % (url, obj.last_message))

    message_link.allow_tags = True


class MessageAdmin(admin.ModelAdmin):
    list_display = ('submission', 'step_id', 'message')


class ResultAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'step', 'message', 'submission_name',
                    'submission_uuid')

    def submission_name(self, obj):
        url = reverse('admin:analytics_automated_submission_change',
                      args=(obj.submission.pk,))
        return '<a href="%s">%s</a>' % (url, obj.submission.submission_name)

    def submission_uuid(self, obj):
        return(obj.submission.UUID)

    submission_name.allow_tags = True
# Register your models here.

admin.site.register(Backend, BackendAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Result, ResultAdmin)
