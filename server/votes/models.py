import uuid
from django.core.exceptions import ValidationError
from django.db import models
from users.models import User
from projects.models import Project

# Create your models here.
class Vote(models.Model):
    ref = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='votes')

    is_overall = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.is_overall:
            if Vote.objects.filter(voter=self.voter, is_overall=True).exclude(pk=self.pk).exists():
                raise ValidationError("You have already voted for overall.")
        else:
            if not self.project.category:
                raise ValidationError("Category must be set for category vote.")
            if Vote.objects.filter(voter=self.voter, category=self.project.category).exclude(pk=self.pk).exists():
                raise ValidationError(f"You have already voted for {self.project.category.name}.")

    def __str__(self):
        return f"{self.voter.email} voted {self.project.title}"
