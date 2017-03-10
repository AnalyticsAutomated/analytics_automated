import re
from django.contrib import admin
from django.core.urlresolvers import reverse

from .models import Backend, Job, Task, Step, Parameter, Result, Validator
from .models import Submission, BackendUser, Message, Environment, QueueType
from .forms import *


class ParameterInline(admin.TabularInline):
    model = Parameter
    extra = 3


class EnvironmentInline(admin.TabularInline):
    model = Environment
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
    extra = 0


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


class ResultInline(admin.TabularInline):
    model = Result
    extra = 0


class QueueTypeAdmin(admin.ModelAdmin):
    fieldsets = []
    list_display = ('name', 'execution_behaviour')


class BackendAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
        # ('Configuration', {'fields': ['server_type', 'ip', 'port']}),
        ('Configuration', {'fields': ['queue_type']}),
        ('Path', {'fields': ['root_path']}),
    ]
    # list_display = ('name', 'server_type', 'ip', 'port', 'root_path')
    list_display = ('name', 'queue_type', 'root_path')
    inlines = [BackendUserInline]


class TaskAdmin(admin.ModelAdmin):
    def processing_backend(self, obj):
        if obj.backend:
            url = reverse('admin:analytics_automated_backend_change',
                          args=(obj.backend.pk,))
            return '<a href="%s">%s</a>' % (url, obj.backend)
        else:
            return 'Backend Unavailable'

    def executable_string(self, obj):
        if obj.backend.queue_type.execution_behaviour == 3:
            return("[R CODE BLOCK]")
        if obj.backend.queue_type.execution_behaviour == 4:
            return("[PYTHON CODE BLOCK]")
        return(obj.executable)

    form = TaskForm
    processing_backend.allow_tags = True

    fieldsets = [
        (None,               {'fields': ['name']}),
        ('Details', {'fields': ['backend', 'description', 'in_glob',
                                'out_glob', 'stdout_glob', 'executable']}),
        ('Job termination behaviour', {'fields': ['incomplete_outputs_behaviour',
                                                  'custom_exit_status',
                                                  'custom_exit_behaviour', ]}),
    ]
    inlines = [ParameterInline, EnvironmentInline]
    list_display = ('name', 'processing_backend', 'in_glob', 'out_glob',
                    'executable_string')

    class Media:
        css = {'all': ('css/task.css', )}


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
        task_list = "No Tasks for job"
        if len(j.steps.all()) > 0:
            task_list = ''

        previous_step_number = None
        for s in j.steps.all():
            url = reverse('admin:analytics_automated_task_change',
                          args=(s.task.pk,))
            if s.ordering == previous_step_number:
                task_list = task_list[:-2]
                task_list += "+"

            task_list += '<a href="%s"> %s </a> ->' % (url, s.task)
            previous_step_number = s.ordering

        task_list = task_list.rstrip(' ->')
        task_list = task_list.rstrip(' +')

        return task_list

    task_list.allow_tags = True


class SubmissionAdmin(admin.ModelAdmin):
    inlines = [ResultInline, MessageInline]
    list_display = ('pk', 'link_to_Job', 'submission_name', 'priority',
                    'email', 'UUID', 'ip', 'status', 'claimed',
                    'last_message', 'step_id', 'created', 'modified')

    def link_to_Job(self, obj):
        if obj.job:
            link = reverse("admin:analytics_automated_job_change",
                           args=[obj.job.id])
            return u'<a href="%s">%s</a>' % (link, obj.job.name)
        else:
            return 'Job does not exist'

    link_to_Job.allow_tags = True


class MessageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'submission_uuid', 'step_id', 'message')

    def submission_uuid(self, obj):
        url = reverse('admin:analytics_automated_submission_change',
                      args=(obj.submission.pk,))
        return '<a href="%s">%s</a>' % (url, obj.submission.UUID)

    submission_uuid.allow_tags = True


class ResultAdmin(admin.ModelAdmin):
    list_display = ('pk', 'link_to_Task', 'step', 'message', 'submission_name',
                    'submission_uuid', 'created')

    def link_to_Task(self, obj):
        if obj.task:
            link = reverse("admin:analytics_automated_task_change",
                           args=[obj.task.id])
            return u'<a href="%s">%s</a>' % (link, obj.task.name)
        else:
            return u'Task no longer exists'

    def submission_name(self, obj):
        url = reverse('admin:analytics_automated_submission_change',
                      args=(obj.submission.pk,))
        return '<a href="%s">%s</a>' % (url, obj.submission.submission_name)

    def submission_uuid(self, obj):
        url = reverse('admin:analytics_automated_submission_change',
                      args=(obj.submission.pk,))
        return '<a href="%s">%s</a>' % (url, obj.submission.UUID)

    submission_name.allow_tags = True
    submission_uuid.allow_tags = True
    link_to_Task.allow_tags = True


# Register your models here.

admin.site.register(Backend, BackendAdmin)
admin.site.register(Task, TaskAdmin)
#admin.site.register(Message, MessageAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Submission, SubmissionAdmin)
#admin.site.register(Result, ResultAdmin)
admin.site.register(QueueType, QueueTypeAdmin)
# gitadmin.site.register(Step
