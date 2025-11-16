# from django.contrib import admin
# from .models import Tag, Job, UserJobMapping

# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ("name", "slug", "created_at", "updated_at",)
#     search_fields = ("name", "slug",)
#     prepopulated_fields = {"slug": ("name",)}
#     ordering = ("name",)


# class UserJobMappingInline(admin.TabularInline):
#     model = UserJobMapping
#     extra = 0
#     readonly_fields = ("user", "status", "created_at", "updated_at")
#     can_delete = False


# @admin.register(Job)
# class JobAdmin(admin.ModelAdmin):
#     list_display = ("title", "company", "job_type", "location", "is_active", "posted_by", "updated_at",)
#     list_filter = ("is_active", "job_type", "location", "tags")
#     search_fields = ("title", "company", "location", "tags__name")
#     ordering = ("-updated_at",)
#     inlines = [UserJobMappingInline]
#     autocomplete_fields = ("posted_by", "tags")
#     list_editable = ("is_active",)


# @admin.register(UserJobMapping)
# class UserJobMappingAdmin(admin.ModelAdmin):
#     list_display = ("user", "job", "status", "created_at", "updated_at")
#     list_filter = ("status",)
#     search_fields = ("user__email", "job__title", "job__company")
#     autocomplete_fields = ("user", "job")
#     ordering = ("-updated_at",)
