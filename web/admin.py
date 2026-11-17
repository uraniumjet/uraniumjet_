from django.contrib import admin

from .models import Enquiry

admin.site.site_header = "Uranium Jet Digital Solution"
admin.site.site_title = "Uranium Jet Digital Solution"
admin.site.index_title = "Enquiries"


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "topic", "email", "phone", "handled", "emailed")
    list_filter = ("handled", "emailed", "topic")
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("created_at", "name", "email", "phone", "topic", "message", "emailed")
    fields = ("created_at", "name", "email", "phone", "topic", "message", "emailed", "handled", "notes")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False
