from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db.models.signals import pre_save, post_save, post_delete
from django.db.models import Q
from django.dispatch import receiver

# NEW
# from accounts.models import User, Student


# project import
from .utils import *
from core.models import ActivityLog

LEARNING = "Learning"
QUIZ = "Quiz"
TEST = "Test"

CATEGORY = (
    (LEARNING, "Learning"),
    (QUIZ, "Quiz"),
    (TEST, "Test"),
)

# LEVEL_COURSE = "Level course"
USER_GUIDE = "User"
IT_PROFESSIONAL = "Professional"

LEVEL = (
    # (LEVEL_COURSE, "Level course"),
    (USER_GUIDE, "User Guide"),
    (IT_PROFESSIONAL, "IT Professional"),
)

FIRST = "First"
SECOND = "Second"
THIRD = "Third"

SEMESTER = (
    (FIRST, "First"),
    (SECOND, "Second"),
    (THIRD, "Third"),
)


class ProgramManager(models.Manager):
    def search(self, query=None):
        queryset = self.get_queryset()
        if query is not None:
            or_lookup = Q(title__icontains=query) | Q(summary__icontains=query)
            queryset = queryset.filter(
                or_lookup
            ).distinct()  # distinct() is often necessary with Q lookups
        return queryset


class Program(models.Model):
    title = models.CharField(max_length=150, unique=True)
    summary = models.TextField(null=True, blank=True)

    objects = ProgramManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("program_detail", kwargs={"pk": self.pk})


@receiver(post_save, sender=Program)
def log_save(sender, instance, created, **kwargs):
    verb = "created" if created else "updated"
    ActivityLog.objects.create(message=f"The program '{instance}' has been {verb}.")


@receiver(post_delete, sender=Program)
def log_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(message=f"The program '{instance}' has been deleted.")


class CourseManager(models.Manager):
    def search(self, query=None):
        queryset = self.get_queryset()
        if query is not None:
            or_lookup = (
                Q(title__icontains=query)
                | Q(summary__icontains=query)
                | Q(code__icontains=query)
                | Q(slug__icontains=query)
            )
            queryset = queryset.filter(
                or_lookup
            ).distinct()  # distinct() is often necessary with Q lookups
        return queryset


class Course(models.Model):
    slug = models.SlugField(blank=True, unique=True)
    title = models.CharField(max_length=200, null=True)
    code = models.CharField(max_length=200, unique=True, null=True)
    credit = models.IntegerField(null=True, default=0)
    summary = models.TextField(max_length=200, blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    level = models.CharField(max_length=25, choices=LEVEL, null=True)
    category = models.CharField(choices=CATEGORY, max_length=200)
    semester = models.CharField(choices=SEMESTER, blank=True, max_length=200)
    is_elective = models.BooleanField(default=False, blank=True, null=True)

    objects = CourseManager()

    def __str__(self):
        return "{0} ({1})".format(self.title, self.code)

    def get_absolute_url(self):
        return reverse("course_detail", kwargs={"slug": self.slug})

    @property
    def is_current_semester(self):
        from core.models import Semester

        current_semester = Semester.objects.get(is_current_semester=True)

        if self.semester == current_semester.semester:
            return True
        else:
            return False


def course_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(course_pre_save_receiver, sender=Course)


@receiver(post_save, sender=Course)
def log_save(sender, instance, created, **kwargs):
    verb = "created" if created else "updated"
    ActivityLog.objects.create(message=f"The course '{instance}' has been {verb}.")


@receiver(post_delete, sender=Course)
def log_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(message=f"The course '{instance}' has been deleted.")


class CourseAllocation(models.Model):
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="allocated_lecturer",
    )
    courses = models.ManyToManyField(Course, related_name="allocated_course")
    session = models.ForeignKey(
        "core.Session", on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return self.lecturer.get_full_name

    def get_absolute_url(self):
        return reverse("edit_allocated_course", kwargs={"pk": self.pk})


class Upload(models.Model):
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to="course_files/",
        help_text="Valid Files: pdf, docx, doc, xls, xlsx, ppt, pptx, zip, rar, 7zip",
        validators=[
            FileExtensionValidator(
                [
                    "pdf",
                    "docx",
                    "doc",
                    "xls",
                    "xlsx",
                    "ppt",
                    "pptx",
                    "zip",
                    "rar",
                    "7zip",
                ]
            )
        ],
    )
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
    upload_time = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)

    def __str__(self):
        return str(self.file)[6:]

    def get_extension_short(self):
        ext = str(self.file).split(".")
        ext = ext[len(ext) - 1]

        if ext in ("doc", "docx"):
            return "word"
        elif ext == "pdf":
            return "pdf"
        elif ext in ("xls", "xlsx"):
            return "excel"
        elif ext in ("ppt", "pptx"):
            return "powerpoint"
        elif ext in ("zip", "rar", "7zip"):
            return "archive"

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)


@receiver(post_save, sender=Upload)
def log_save(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            message=f"The file '{instance.title}' has been uploaded to the course '{instance.course}'."
        )
    else:
        ActivityLog.objects.create(
            message=f"The file '{instance.title}' of the course '{instance.course}' has been updated."
        )


@receiver(post_delete, sender=Upload)
def log_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(
        message=f"The file '{instance.title}' of the course '{instance.course}' has been deleted."
    )


class UploadVideo(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video = models.FileField(
        upload_to="course_videos/",
        help_text="Valid video formats: mp4, mkv, wmv, 3gp, f4v, avi, mp3",
        validators=[
            FileExtensionValidator(["mp4", "mkv", "wmv", "3gp", "f4v", "avi", "mp3"])
        ],
    )
    summary = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse(
            "video_single", kwargs={"slug": self.course.slug, "video_slug": self.slug}
        )

    def delete(self, *args, **kwargs):
        self.video.delete()
        super().delete(*args, **kwargs)


def video_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
        

pre_save.connect(video_pre_save_receiver, sender=UploadVideo)


# NEW
class VideoWatchProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video = models.ForeignKey(UploadVideo, on_delete=models.CASCADE)
    watched = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'video')  # Ensure a user has only one entry per video

    def __str__(self):
        return f"{self.user.username} - {self.video.title} - {'Watched' if self.watched else 'Not Watched'}"


# New Model to Track Course Completion
class CourseProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)  # Indicates if user has completed all videos

    class Meta:
        unique_together = ('user', 'course')  # Ensure unique record per user per course

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {'Completed' if self.completed else 'Not Completed'}"

# END


@receiver(post_save, sender=UploadVideo)
def log_save(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            message=f"The video '{instance.title}' has been uploaded to the course {instance.course}."
        )
    else:
        ActivityLog.objects.create(
            message=f"The video '{instance.title}' of the course '{instance.course}' has been updated."
        )


@receiver(post_delete, sender=UploadVideo)
def log_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(
        message=f"The video '{instance.title}' of the course '{instance.course}' has been deleted."
    )


class CourseOffer(models.Model):
    """NOTE: Only department head can offer semester courses"""

    dep_head = models.ForeignKey("accounts.DepartmentHead", on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.dep_head)
