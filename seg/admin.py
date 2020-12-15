from django.contrib import admin

# Register your models here.
class PaisAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado')
    ordering = ('nombre',)
    search_fields = ('nombre',)


class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('pais', 'nombre',)
    ordering = ('pais', 'nombre',)
    search_fields = ('nombre',)


class CantonAdmin(admin.ModelAdmin):
    list_display = ('provincia', 'nombre',)
    ordering = ('provincia', 'nombre',)
    search_fields = ('nombre',)


from seg.models import Pais, Provincia, Canton

admin.site.register(Pais, PaisAdmin)
admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(Canton, CantonAdmin)
