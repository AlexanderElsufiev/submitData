
from django.contrib import admin
from .models import * #PerevalAdded, PerevalUser, PerevalCoords, PerevalImage, PerevalImageAsIs


@admin.register(PerevalUser)
class PerevalUserAdmin(admin.ModelAdmin):
    list_display = ('fam', 'name', 'otc', 'email', 'phone')
    list_filter = ('fam',)
    search_fields = ('fam', 'name', 'email')

@admin.register(PerevalCoords)
class CoordsAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'height')

class PerevalImageInline(admin.TabularInline):
    model = PerevalImage
    extra = 1


@admin.register(PerevalAdded)
class PerevalAddedAdmin(admin.ModelAdmin):
    list_display = ('title', 'beauty_title', 'user', 'add_time', 'date_added')
    list_filter = ('add_time', 'date_added')
    search_fields = ('title', 'beauty_title', 'other_titles')
    readonly_fields = ('date_added',)
    inlines = [PerevalImageInline]


@admin.register(PerevalImageAsIs)
class PerevalImageAsIsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)


@admin.register(PerevalImage)
class PerevalImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'pereval', 'image')
    list_filter = ('pereval',)
