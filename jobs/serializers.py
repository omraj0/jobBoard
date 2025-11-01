from rest_framework import serializers
from .models import Job, Tag

class JobManagementSerializer(serializers.ModelSerializer):
    posted_by = serializers.CharField(source='posted_by.first_name', read_only=True)
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Job
        fields = ('id', 'title', 'company', 'location', 'description', 'application_link', 'job_type', 'is_active', 'posted_by', 'created_at', 'updated_at', 'tags',)
        read_only_fields = ('posted_by', 'created_at', 'updated_at')