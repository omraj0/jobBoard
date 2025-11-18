from django.urls import path
from .views import JobListView, JobFilterView, JobDetailView, MyJobsView, JobManagementListCreateView, JobManagementDetailView

urlpatterns = [
    path('', JobListView.as_view(), name='job-list'),
    path('filter/', JobFilterView.as_view(), name='job-filter'),
    path('<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    path('my-jobs/', MyJobsView.as_view(), name='my-jobs'),
    path('manage/', JobManagementListCreateView.as_view(), name='job-manage-list-create'),
    path('manage/<int:pk>/', JobManagementDetailView.as_view(), name='job-manage-detail'),
]