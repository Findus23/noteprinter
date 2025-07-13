from django.contrib import admin

from notes.models import Note, NoteImage


class NoteImageInline(admin.StackedInline):
    model = NoteImage
    readonly_fields = ["image_preview", "pdf_file","width","height","created_at"]

class NoteAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at", "last_updated_at", "printed_at"]
    list_display = ["text", "created_at", "last_updated_at", "printed_at"]
    search_fields = ["text"]
    list_filter = ["created_at", "printed_at", "last_updated_at"]
    date_hierarchy = "printed_at"
    save_on_top = True
    inlines = [NoteImageInline]


admin.site.register(Note, NoteAdmin)

admin.site.register(NoteImage)
