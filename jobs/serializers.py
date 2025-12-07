from .models import Job, Tag
from jobBoard.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'slug']


class FilterSerializer(serializers.Serializer):
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    title = serializers.ListField(child=serializers.CharField(), required=False)
    company = serializers.ListField(child=serializers.CharField(), required=False)
    location = serializers.ListField(child=serializers.CharField(), required=False)
    job_type = serializers.ListField(child=serializers.CharField(), required=False)
    time = serializers.ListField(child=serializers.CharField(), required=False)


class JobListSerializer(serializers.ModelSerializer):
    posted_by = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = ('id', 'title', 'company', 'location', 'job_type', 'posted_by', 'tags', 'created_at', 'updated_at',)
        read_only_fields = ('created_at', 'updated_at')


class JobDetailSerializer(serializers.ModelSerializer):
    posted_by = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = ('id', 'title', 'company', 'location', 'description', 'application_link', 'job_type', 'posted_by', 'tags', 'created_at', 'updated_at',)
        read_only_fields = ('created_at', 'updated_at')


class JobManagementSerializer(serializers.ModelSerializer):
    posted_by = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = ('id', 'title', 'company', 'location', 'description', 'application_link', 'job_type', 'is_active', 'posted_by', 'created_at', 'updated_at', 'tags',)
        read_only_fields = ('posted_by', 'created_at', 'updated_at')

    def create(self, validated_data):
        tags = self.context.get("tags", [])
        job = Job.objects.create(**validated_data)
        if tags:
            job.tags.set(tags)
        return job