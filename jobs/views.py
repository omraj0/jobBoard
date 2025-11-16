from datetime import timedelta
from django.http import Http404
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Job, Tag
from .permissions import CanManageJobs
from .serializers import JobListSerializer, JobDetailSerializer, JobManagementSerializer, FilterSerializer


class JobListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Job.objects.filter(is_active=True).select_related('posted_by')
        serializer = JobListSerializer(queryset, many=True)
        filters_data = {
            'tags': set(Tag.objects.values_list('name', flat=True)),
            'title': set(Job.objects.values_list('title', flat=True)),
            'company': set(Job.objects.values_list('company', flat=True)),
            'location': set(Job.objects.exclude(location__exact='').values_list('location', flat=True)),
            'job_type': [choice[0] for choice in Job.JobType.choices],
            'time': ["last_6", "last_24", "this_week", "this_month", "all"]
        }

        filter_serializer = FilterSerializer(filters_data)
        return Response({
            'filters': filter_serializer.data,
            'jobs': serializer.data
        }, status=status.HTTP_200_OK)


class JobFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        filters = {}
        tags = request.data.get("tags", [])
        titles = request.data.get("title", [])
        companies = request.data.get("company", [])
        locations = request.data.get("location", [])
        job_types = request.data.get("job_type", [])
        time_filter = request.data.get("time", None)

        if job_types:
            filters["job_type__in"] = job_types if isinstance(job_types, list) else [job_types]
        if locations:
            filters["location__in"] = locations if isinstance(locations, list) else [locations]
        if companies:
            filters["company__in"] = companies if isinstance(companies, list) else [companies]
        if titles:
            filters["title__in"] = titles if isinstance(titles, list) else [titles]
        if tags:
            filters["tags__name__in"] = tags

        queryset = Job.objects.filter(is_active=True, **filters)

        now = timezone.now()
        if time_filter == "last_6":
            queryset = queryset.filter(created_at__gte=now - timedelta(hours=6))
        elif time_filter == "last_24":
            queryset = queryset.filter(created_at__gte=now - timedelta(hours=24))
        elif time_filter == "this_week":
            queryset = queryset.filter(created_at__gte=now - timedelta(days=7))
        elif time_filter == "this_month":
            queryset = queryset.filter(created_at__gte=now - timedelta(days=30))

        queryset = queryset.distinct().select_related('posted_by').order_by('-updated_at')
        serializer = JobListSerializer(queryset, many=True)

        filters_data = {
            'tags': set(Tag.objects.values_list('name', flat=True)),
            'title': set(Job.objects.values_list('title', flat=True)),
            'company': set(Job.objects.values_list('company', flat=True)),
            'location': set(Job.objects.exclude(location__exact='').values_list('location', flat=True)),
            'job_type': [choice[0] for choice in Job.JobType.choices],
            'time': ["last_6", "last_24", "this_week", "this_month", "all"]
        }

        filter_serializer = FilterSerializer(filters_data)
        return Response({
            'filters': filter_serializer.data,
            'jobs': serializer.data
        }, status=status.HTTP_200_OK)


class JobDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Job.objects.get(pk=pk, is_active=True)
        except Job.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        job = self.get_object(pk)
        serializer = JobDetailSerializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk, *args, **kwargs):
        action = request.data.get("action")
        job = self.get_object(pk)

        if action == "activity":
            activity = request.data.get("activity")
            if activity not in ["Clicked", "Applied", "Bookmarked"]:
                return Response({"detail": "Invalid activity."}, status=status.HTTP_400_BAD_REQUEST)
            
            mapping, created = job.job_users.get_or_create(
                user=request.user,
                defaults={'status': activity}
            )
            if not created:
                mapping.status = activity
                mapping.save()
            return Response({"detail": f"Job {activity} successfully."}, status=status.HTTP_200_OK)


class JobManagementListCreateView(APIView):
    permission_classes = [IsAuthenticated, CanManageJobs]

    # def get(self, request, *args, **kwargs):
    #     user = request.user
    #     queryset = Job.objects.none()
    #     if user.is_superuser:
    #         queryset = Job.objects.all().select_related('posted_by')
    #     elif user.is_staff:
    #         queryset = Job.objects.filter(posted_by=user).select_related('posted_by')

    #     serializer = JobManagementSerializer(queryset, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

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