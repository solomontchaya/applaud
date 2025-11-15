from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    project_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description',
            'created_at', 'updated_at',
            'project_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'project_count']

    def get_project_count(self, obj):
        return obj.project_set.count()  # assuming Project has category = ForeignKey(Category)

    def validate_name(self, value):
        if self.instance:
            if Category.objects.filter(name__iexact=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("A category with this name already exists.")
        else:
            if Category.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError("A category with this name already exists.")
        return value.strip().title()