from django.db import models
import bugsnag

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating ``created``
    and ``modified`` fields.

    use with
    class Flavor(TimeStampedModel):
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Create your models here.
class Backend(models.Model):
    # Handling choices
    # http://www.b-list.org/weblog/2007/nov/02/handle-choices-right-way/
    LOCALHOST = 1
    GRIDENGINE = 2
    RSERVE = 3
    HADOOP = 4
    NUMPY = 5
    SERVER_CHOICES = (
        (LOCALHOST, "localhost"),
        (GRIDENGINE, "GridEngine"),
        (RSERVE, "RServe"),
        # add more when more backends are complete
    )
    name        = models.CharField(max_length=64, unique=True, null=False, blank=False)
    server_type = models.IntegerField(null=False, blank=False, choices=SERVER_CHOICES, default=LOCALHOST)
    ip          = models.GenericIPAddressField(default="127.0.0.1", null=False, blank=False)
    port        = models.IntegerField(default=80, null=False, blank=False)
    root_path   = models.CharField(max_length=256, null=False, default="/tmp/", blank=False)

    def __str__(self):
        return self.name
# TODO:Not clear if the path to the processed file root should be in the
# backend or in the task table. I guess it is more of a property of the
# backend though This will likely expand lots as we understand the complexity
# of the backend set ups. adding it to task allows tasks to write to different
# places, the backend would be the default location in that instance.


class Job(models.Model):
    name        = models.CharField(max_length=64, unique=True, null=False, blank=False)
    runnable    = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return self.name
# TODO: set runnable true if all it's tasks exists, set false if a task
# needed has been deleted


class Task(models.Model):
    backend     = models.ForeignKey(Backend, on_delete=models.SET_NULL, null=True)
    name        = models.CharField(max_length=64, unique=True, null=False, blank=False)
    in_glob     = models.CharField(max_length=64, null=False, blank=False)
    out_glob    = models.CharField(max_length=64, null=False, blank=False)
    executable  = models.CharField(max_length=256,null=False, blank=False)
    def __str__(self):
        return self.name
# TODO: add 2 tables to let tasks have multiple inputs and multiple outputs
# TODO: deleting a task should delete all it's params and set any jobs to
# runnable false where it is missing


class Step(models.Model):
    job         = models.ForeignKey(Job,related_name='steps')
    task        = models.ForeignKey(Task)
    ordering    = models.IntegerField(default=0, null=False, blank=False)

    def __str__(self):
        return str(self.task)

    class Meta:
      unique_together = ('job', 'ordering',)


class Parameter(models.Model):
    task        = models.ForeignKey(Task)
    flag        = models.CharField(max_length=64, null=False, blank=False)
    default     = models.CharField(max_length=64, null=True, blank=False)
    bool_valued = models.BooleanField(default=False, blank=False)
    rest_alias  = models.CharField(max_length=64, unique=True, null=False, blank=False)

    def __str__(self):
        return self.flag

class Queue(models.Model):
    job         = models.ForeignKey(Job)
    UUID        = models.CharField(max_length=64,unique=True, null=False, blank=False)
    input_data  = models.BinaryField(null=True)
    status      = models.IntegerField(null=False, blank=False)
    email       = models.CharField(max_length=256, null=False, blank=False)
    mobile      = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.name
# TODO: change the blob to type upload type


class Result(models.Model):
    UUID        = models.ForeignKey(Queue,to_field='UUID')
    result_data = models.BinaryField(null=False)

    def __str__(self):
        return self.name
# TODO: add appropriate validation
