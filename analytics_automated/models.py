from django.db import models


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
    name = models.CharField(max_length=64, unique=True, null=False, blank=False, db_index=True)
    server_type = models.IntegerField(null=False, blank=False, choices=SERVER_CHOICES, default=LOCALHOST)
    ip = models.GenericIPAddressField(default="127.0.0.1", null=False, blank=False)
    port = models.IntegerField(default=80, null=False, blank=False)
    root_path = models.CharField(max_length=256, null=False, default="/tmp/", blank=False)

    def __str__(self):
        return self.name
# TODO:Not clear if the path to the processed file root should be in the
# backend or in the task table. I guess it is more of a property of the
# backend though This will likely expand lots as we understand the complexity
# of the backend set ups. adding it to task allows tasks to write to different
# places, the backend would be the default location in that instance.


class Job(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False, blank=False, db_index=True)
    runnable = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return self.name
# TODO: set runnable true if all it's tasks exists, set false if a task
# needed has been deleted


class Task(models.Model):
    backend = models.ForeignKey(Backend, on_delete=models.SET_NULL, null=True, related_name='tasks')
    name = models.CharField(max_length=64, unique=True, null=False, blank=False)
    in_glob = models.CharField(max_length=64, null=False, blank=False)
    out_glob = models.CharField(max_length=64, null=False, blank=False)
    executable = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.name
# TODO: add 2 tables to let tasks have multiple inputs and multiple outputs
# TODO: deleting a task should delete all it's params and set any jobs to
# runnable false where it is missing


class Step(models.Model):
    job = models.ForeignKey(Job, related_name='steps')
    task = models.ForeignKey(Task)
    ordering = models.IntegerField(default=0, null=False, blank=False)

    def __str__(self):
        return str(self.task)

    class Meta:
        unique_together = ('job', 'ordering',)


class Parameter(models.Model):
    task = models.ForeignKey(Task)
    flag = models.CharField(max_length=64, null=False, blank=False)
    default = models.CharField(max_length=64, null=True, blank=False)
    bool_valued = models.BooleanField(default=False, blank=False)
    rest_alias = models.CharField(max_length=64, unique=True, null=False, blank=False)

    def __str__(self):
        return self.flag

    def save(self, *args, **kwargs):
        self.rest_alias = str(self.task)+"_"+self.rest_alias
        super(Parameter, self).save(*args, **kwargs)


class Submission(TimeStampedModel):
    SUBMITTED = 0  # a job has been submitted but no worker has claimed it
    RUNNING = 1    # job submitted and worker has claimed it
    COMPLETE = 2   # All tasks complete and results available
    ERROR = 3      # A task has failed, the job has stopped
    CRASH = 4      # Something crashed, went away of segfaulted in some way
                   # the job has stopped
    STATUS_CHOICES = (
        (SUBMITTED, "Submitted"),
        (RUNNING, "Running"),
        (COMPLETE, "Complete"),
        (ERROR, "Error"),
        (CRASH, "Crash"),
    )
    job = models.ForeignKey(Job)
    submission_name = models.CharField(max_length=64, null=False, blank=False)
    UUID = models.CharField(max_length=64, unique=True, null=True, blank=False, db_index=True)
    email = models.EmailField(max_length=256, null=True, blank=False)
    ip = models.GenericIPAddressField(default="127.0.0.1", null=False, blank=False)
    input_data = models.FileField(blank=False)
    status = models.IntegerField(null=False, blank=False, choices=STATUS_CHOICES, default=SUBMITTED)
    message = models.CharField(max_length=256, null=True, blank=True, default="Submitted")
    claimed = models.BooleanField(null=False, default=False)
    worker_id = models.IntegerField(blank=True, null=True, default=None)

    def __str__(self):
        return str(self.pk)


class Result(models.Model):
    submission = models.ForeignKey(Submission)
    task = models.ForeignKey(Task)
    result_data = models.FileField(null=False)
    name = models.CharField(max_length=64, null=True, blank=False)
    message = models.CharField(max_length=256, null=True, blank=True, default="Submitted")

    def __str__(self):
        return self.name
# TODO: add appropriate validation
