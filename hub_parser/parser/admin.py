from django.contrib import admin
from django.utils.html import format_html

from .models import Articles


class ArticlesAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'date', 'author', 'authorlink', 'postlink', 'hubs', "delete_button"]
    list_display_links = ["id", "title"]
    search_fields = ["title", 'author', 'date']
    save_on_top = True

    @staticmethod
    def delete_button(obj):
        return format_html('<a class="btn" href="/admin/parser/articles/{}/delete/">Delete</a>', obj.id)


admin.site.register(Articles, ArticlesAdmin)
