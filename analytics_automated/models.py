import re
from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError


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


class QueueType(models.Model):
    # Handling choices
    # http://www.b-list.org/weblog/2007/nov/02/handle-choices-right-way/
    LOCALHOST = 1
    GRIDENGINE = 2
    R = 3
    PYTHON = 4
    EXECUTION_CHOICES = (
        (LOCALHOST, "localhost"),
        (GRIDENGINE, "GridEngine"),
        (R, "R"),
        (PYTHON, "Python")
        # add more when more backends are complete
    )
    name = models.CharField(max_length=512, null=True, blank=True, unique=True)
    execution_behaviour = models.IntegerField(null=False, blank=False,
                                              choices=EXECUTION_CHOICES,
                                              default=LOCALHOST)

    def __str__(self):
        return self.name


# Create your models here.
class Backend(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False,
                            blank=False, db_index=True)
    queue_type = models.ForeignKey(QueueType, on_delete=models.SET_NULL,
                                   null=True,
                                   related_name='queues')
    # removing log in details as remote backend is NOT YET IMPLEMENTED
    # ip = models.GenericIPAddressField(default="127.0.0.1", null=False,
    #                                   blank=False)
    # port = models.IntegerField(default=80, null=False, blank=False)
    root_path = models.CharField(max_length=256, null=False, default="/tmp/",
                                 blank=False)

    def __str__(self):
        return self.name
# TODO:Not clear if the path to the processed file root should be in the
# backend or in the task table. I guess it is more of a property of the
# backend though This will likely expand lots as we understand the complexity
# of the backend set ups. adding it to task allows tasks to write to different
# places, the backend would be the default location in that instance.


class BackendUser(models.Model):
    # Handling choices
    # http://www.b-list.org/weblog/2007/nov/02/handle-choices-right-way/
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    PRIORITY_CHOICES = (
        (LOW, "low"),
        (MEDIUM, "medium"),
        (HIGH, "high"),
        # add more when more backends are complete
    )
    backend = models.ForeignKey(Backend, on_delete=models.SET_NULL, null=True,
                                related_name='users')
    login_name = models.CharField(max_length=64, unique=True, null=False,
                                  blank=False, db_index=True)
    password = models.CharField(max_length=64, unique=True, null=False,
                                blank=False, db_index=True)
    priority = models.IntegerField(null=False, blank=False,
                                   choices=PRIORITY_CHOICES,
                                   default=MEDIUM)


class Job(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False,
                            blank=False, db_index=True)
    runnable = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('pk', )
# TODO: set runnable true if all it's tasks exists, set false if a task
# needed has been deleted


class ValidatorTypes(models.Model):
    name = models.CharField(max_length=512, null=True, blank=True, unique=True)

    def __str__(self):
        return self.name


class Validator(models.Model):

    def validate_re_string(value):
        is_valid = False
        try:
            re.compile(value)
            is_valid = True
        except re.error:
            is_valid = False
        if is_valid is False:
            raise(ValidationError("REGULAR EXPRESSION IS NOT VALID: " +
                                  value))

    job = models.ForeignKey(Job, related_name="validators",
                            on_delete=models.CASCADE)
    validation_type = models.ForeignKey(ValidatorTypes,
                                        on_delete=models.CASCADE)

    def __str__(self):
        return self.validation_type.name


class Task(models.Model):
    CONTINUE = 0   # The task should continue to the next step
    TERMINATE = 1  # The task should terminate
    FAIL = 3       # The task should terminate and raise an error
    #                the job has stopped
    COMPLETION_CHOICES = (
        (CONTINUE, "Continue Running Tasks"),
        (TERMINATE, "Stop Running Tasks (do not raise error)"),
        (FAIL, "Stop Running Tasks (raise error)")
    )
    backend = models.ForeignKey(Backend, on_delete=models.SET_NULL, null=True,
                                related_name='tasks', blank=False)
    name = models.CharField(max_length=64, unique=True, null=False,
                            blank=False)
    description = models.CharField(max_length=256, null=True)
    in_glob = models.CharField(max_length=256, null=False, blank=False)
    out_glob = models.CharField(max_length=256, null=False, blank=False)
    stdout_glob = models.CharField(max_length=256, null=True)
    executable = models.CharField(max_length=8192, null=False, blank=False)
    incomplete_outputs_behaviour = models.IntegerField(null=False, blank=False,
                                                       choices=COMPLETION_CHOICES,
                                                       default=FAIL)
    custom_exit_status = models.CharField(max_length=256, null=True,
                                          blank=True)
    custom_exit_behaviour = models.IntegerField(null=True, blank=True,
                                                choices=COMPLETION_CHOICES,)

    def __str__(self):
        return self.name
# TODO: deleting a task should set any jobs to runnable false where it is
# missing


#Attach to a task some config information if the user wants to add this
class Configuration(models.Model):
    SOFTWARE = 0
    DATASET = 1
    MISC = 2
    CONFIGURATION_CHOICES = {
        (SOFTWARE, "Software"),
        (DATASET, "Dataset"),
        (MISC, "Misc."),
    }
    task = models.ForeignKey(Task, null=False, related_name="configuration",
                             on_delete=models.CASCADE)
    type = models.IntegerField(null=True, blank=True,
                               choices=CONFIGURATION_CHOICES,
                               default=SOFTWARE)
    name = models.CharField(max_length=256, null=True, blank=True)
    parameters = models.CharField(max_length=256, null=True, blank=True)
    version = models.CharField(max_length=256, null=True, blank=True)

    def returnType(self):
        d = dict(Configuration.CONFIGURATION_CHOICES)
        return(d[self.type])


class Step(models.Model):
    job = models.ForeignKey(Job, related_name='steps',
                            on_delete=models.CASCADE)
    task = models.ForeignKey(Task, null=True,
                             on_delete=models.CASCADE)
    ordering = models.IntegerField(default=0, null=False, blank=False)

    def __str__(self):
        return str(self.task)

    class Meta:
        ordering = ['ordering']


class Environment(models.Model):
    task = models.ForeignKey(Task, related_name='environment',
                             on_delete=models.CASCADE)
    env = models.CharField(max_length=129, null=True, blank=False)
    value = models.CharField(max_length=2048, null=True, blank=False)

    def __str__(self):
        return self.env


class Parameter(models.Model):
    task = models.ForeignKey(Task, related_name='parameters',
                             on_delete=models.CASCADE)
    flag = models.CharField(max_length=64, null=False, blank=False)
    default = models.CharField(max_length=64, null=True, blank=False)
    bool_valued = models.BooleanField(default=False, blank=False)
    rest_alias = models.CharField(max_length=64, unique=True, null=False,
                                  blank=False)
    spacing = models.BooleanField(default=True, blank=False)
    switchless = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return self.flag

    def save(self, *args, **kwargs):
        self.rest_alias = str(self.task)+"_"+self.rest_alias
        super(Parameter, self).save(*args, **kwargs)


class Batch(models.Model):
    SUBMITTED = 0  # a job has been submitted but no worker has claimed it
    RUNNING = 1    # job submitted and worker has claimed it
    COMPLETE = 2   # All tasks complete and results available
    ERROR = 3      # A task has failed, the job has stopped
    CRASH = 4      # Something crashed, went away of segfaulted in some way
    #                the job has stopped
    STATUS_CHOICES = (
        (SUBMITTED, "Submitted"),
        (RUNNING, "Running"),
        (COMPLETE, "Complete"),
        (ERROR, "Error"),
        (CRASH, "Crash"),
    )
    UUID = models.CharField(max_length=64, unique=False, null=True,
                            blank=False, db_index=True)
    status = models.IntegerField(null=False, blank=False,
                                 choices=STATUS_CHOICES, default=SUBMITTED)

    def __str__(self):
        return self.UUID

    @transaction.atomic
    def update_batch_state(b, new_status):
        if b.status != Batch.ERROR and b.status != Batch.CRASH:
            b.status = new_status
            b.save()

    def returnStatus(self):
        d = dict(Batch.STATUS_CHOICES)
        return(d[self.status])


class Submission(TimeStampedModel):
    SUBMITTED = 0  # a job has been submitted but no worker has claimed it
    RUNNING = 1    # job submitted and worker has claimed it
    COMPLETE = 2   # All tasks complete and results available
    ERROR = 3      # A task has failed, the job has stopped
    CRASH = 4      # Something crashed, went away of segfaulted in some way
    #                the job has stopped
    STATUS_CHOICES = (
        (SUBMITTED, "Submitted"),
        (RUNNING, "Running"),
        (COMPLETE, "Complete"),
        (ERROR, "Error"),
        (CRASH, "Crash"),
    )

    LOW = 0
    MEDIUM = 1
    HIGH = 2
    PRIORITY_CHOICES = (
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
    )

    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True,)
    submission_name = models.CharField(max_length=64, null=False, blank=False)
    UUID = models.CharField(max_length=64, unique=True, null=True, blank=False,
                            db_index=True)
    priority = models.IntegerField(null=False, blank=False,
                                   choices=PRIORITY_CHOICES, default=MEDIUM)
    email = models.EmailField(max_length=256, null=True, blank=False)
    ip = models.GenericIPAddressField(default="127.0.0.1", null=False,
                                      blank=False)
    input_data = models.FileField(blank=False)
    status = models.IntegerField(null=False, blank=False,
                                 choices=STATUS_CHOICES, default=SUBMITTED)
    last_message = models.CharField(max_length=2046, null=True, blank=True,
                                    default="Submitted")
    claimed = models.BooleanField(null=False, default=False)
    worker_id = models.CharField(max_length=64, blank=True, null=True,
                                 default=None)
    hostname = models.CharField(max_length=256, blank=True, null=True,
                                default=None)
    step_id = models.IntegerField(null=True, blank=False)
    batch = models.ForeignKey(Batch, null=True, related_name='submissions',
                              on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pk)

    def returnStatus(self):
        d = dict(Submission.STATUS_CHOICES)
        return(d[self.status])

    @transaction.atomic
    def update_submission_state(s, claim, new_status, step, id, message, host):
        """
            Updates the Submission object with some book keeping
        """
        s.claimed = claim
        s.status = new_status
        s.last_message = message
        s.worker_id = id
        s.step_id = step
        s.hostname = host
        s.save()
        m = Message.objects.create(submission=s,
                                   step_id=step,
                                   message=message)
        m.save()


# Store results data
class Result(TimeStampedModel):
    submission = models.ForeignKey(Submission, related_name='results',
                                   on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
    step = models.IntegerField(null=False, blank=False)
    previous_step = models.IntegerField(null=True, blank=False)
    result_data = models.FileField(null=False)
    name = models.CharField(max_length=64, null=True, blank=False)
    message = models.CharField(max_length=256, null=True, blank=True,
                               default="Submitted")

    def __str__(self):
        return self.name


# keep a timestamped history of all the messages sent for this jobs
class Message(TimeStampedModel):
    submission = models.ForeignKey(Submission, related_name='messages',
                                   on_delete=models.CASCADE)
    step_id = models.IntegerField(null=True, blank=False)
    message = models.CharField(max_length=2046, null=True, blank=True,
                               default="Submitted")

    def __str__(self):
        return str(self.pk)
