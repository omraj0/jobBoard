from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Job, Tag
from .permissions import CanManageJobs
from .serializers import JobManagementSerializer


class JobManagementListCreateView(APIView):
    permission_classes = [IsAuthenticated, CanManageJobs]

    def get(self, request, *args, **kwargs):
        """
        Implements the LIST logic from the ViewSet's get_queryset.
        """
        user = request.user
        queryset = Job.objects.none()
        if user.is_superuser:
            queryset = Job.objects.all().select_related('posted_by')
        elif user.is_staff:
            queryset = Job.objects.filter(posted_by=user).select_related('posted_by')

        serializer = JobManagementSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        tags_new = []
        tags = request.data.get('tags', [])
        for tag in tags:
            tag = tag.strip().lower()
            tag_obj, _ = Tag.objects.get_or_create(name=tag)
            tags_new.append(tag_obj)

        request.data["tags"] = [tag.slug for tag in tags_new]
        serializer = JobManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(posted_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobManagementDetailView(APIView):
    permission_classes = [IsAuthenticated, CanManageJobs]

    def _get_object(self, pk):
        try:
            obj = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            raise Http404
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, pk, *args, **kwargs):
        job = self._get_object(pk)
        serializer = JobManagementSerializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk, *args, **kwargs):
        job = self._get_object(pk)
        if request.data.get("action") == "delete":
            job.delete()
            return Response({"detail": "Job deleted successfully."}, status=status.HTTP_200_OK)

        tags_new = []
        tags = request.data.get('tags', [])
        for tag in tags:
            tag = tag.strip().lower()
            tag_obj, _ = Tag.objects.get_or_create(name=tag)
            tags_new.append(tag_obj)

        request.data["tags"] = [tag.slug for tag in tags_new]
        serializer = JobManagementSerializer(job, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)