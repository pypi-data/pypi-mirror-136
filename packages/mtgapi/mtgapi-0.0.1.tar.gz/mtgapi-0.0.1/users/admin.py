from django.contrib import admin
from . import models  
# # from guardian.admin import GuardedModelAdmin




# # With object permissions support
# class AuthorAdmin(GuardedModelAdmin):
#     pass

# admin.site.register(Author, AuthorAdmin)
admin.site.register(models.User)