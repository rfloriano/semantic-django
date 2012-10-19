from django.contrib import admin

from example_project.example_app.smodels import BasePrograma


class BaseProgramaAdmin(admin.ModelAdmin):
    readonly_fields = ['uri']

admin.site.register(BasePrograma, BaseProgramaAdmin)
