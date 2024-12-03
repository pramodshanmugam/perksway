from django.db import models
from django.conf import settings
from users.models import CustomUser  

class Class(models.Model):
    name = models.CharField(max_length=100)
    class_code = models.CharField(max_length=10, unique=True)  # Unique class code
    description = models.TextField(null=True, blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='classes')
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='joined_classes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    class_ref = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='groups')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="joined_groups")  # Existing field for joined students

    # New fields for added functionality
    requires_approval = models.BooleanField(default=False)  # If approval is required for joining
    max_students = models.PositiveIntegerField(default=0)  # Maximum number of students allowed in the group
    pending_approvals = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="pending_groups", blank=True) 

    def __str__(self):
        return f"{self.name} - {self.class_ref.name}"
