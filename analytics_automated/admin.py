from django.contrib import admin
from django.core.urlresolvers import reverse
from analytics_automated.models import Backend, Job, Task, Step, Parameter, Queue, Result

class ParameterInline(admin.TabularInline):
    model = Parameter
    extra = 3

class StepInline(admin.TabularInline):
    model = Step
    extra = 3

class BackendAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('Configuration', {'fields': ['server_type','ip','port']}),
        ('Path', {'fields': ['root_path']}),
    ]
    list_display = ('name','server_type','ip','port','root_path')

class TaskAdmin(admin.ModelAdmin):
    def processing_backend(self, obj):
        url = reverse('admin:analytics_automated_backend_change', args=(obj.pk,))
        return '<a href="%s">%s</a>' % (url, obj.backend)
    processing_backend.allow_tags = True

    fieldsets = [
        (None,               {'fields': ['name']}),
        ('Details', {'fields': ['backend','name','in_glob','out_glob','executable']}),
    ]
    inlines = [ParameterInline]
    list_display = ('name','processing_backend','executable')


class JobAdmin(admin.ModelAdmin):
    inlines = [StepInline]
    list_display = ('name','runnable','number_of_tasks','task_list')
    def number_of_tasks(self,obj):
        j = Job.objects.get(pk=obj.pk)
        return '%d' % j.steps.count()
    def task_list(self,obj):
        j = Job.objects.get(pk=obj.pk)
        task_list = ""
        for s in j.steps.all():
            url = reverse('admin:analytics_automated_task_change', args=(s.task.pk,))
            task_list += '<a href="%s"> %s </a> ->' % (url, s.task)
        task_list = task_list.rstrip(' ->')
        return task_list
    task_list.allow_tags = True



admin.site.register(Backend, BackendAdmin)
admin.site.register(Task,TaskAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Queue)
admin.site.register(Result)

# Register your models here.
