from django.db import models
from django.conf import settings
from django.utils.text import slugify
from jobBoard.models import TimestampedModel

class Tag(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    
class Job(TimestampedModel):
    class JobType(models.TextChoices):
        FULL_TIME = 'Full-time', 'Full-time'
        PART_TIME = 'Part-time', 'Part-time'
        CONTRACT = 'Contract', 'Contract'
        INTERNSHIP = 'Internship', 'Internship'

    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs_posted')
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME, db_index=True)

    title = models.CharField(max_length=200, db_index=True)
    company = models.CharField(max_length=200, db_index=True)
    location = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    application_link = models.URLField(max_length=800)
    is_active = models.BooleanField(default=True, db_index=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='jobs')

    class Meta:
        ordering = ("-updated_at",)
        indexes = [
            models.Index(fields=["is_active", "location", "job_type"]),
            models.Index(fields=["is_active", "updated_at"]),
            models.Index(fields=["title", "company"]),
        ]

    def __str__(self):
        return f"{self.title} at {self.company}"
    

class UserJobMapping(TimestampedModel):
    class Status(models.TextChoices):
        CLICKED = "Clicked", "Clicked"
        APPLIED = "Applied", "Applied"
        BOOKMARKED = "Bookmarked", "Bookmarked"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_jobs')
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='job_users')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CLICKED)

    class Meta:
        unique_together = ("user", "job")
        ordering = ("-updated_at",)

    def __str__(self):
        return f"{self.user.email} - {self.job.title} [{self.status}]"