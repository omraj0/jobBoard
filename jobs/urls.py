from django.urls import path
from .views import JobManagementListCreateView, JobManagementDetailView

urlpatterns = [
    path('manage/', JobManagementListCreateView.as_view(), name='job-manage-list-create'),
    path('manage/<int:pk>/', JobManagementDetailView.as_view(), name='job-manage-detail'),
]