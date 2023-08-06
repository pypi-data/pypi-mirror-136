from django.contrib import admin
from mtx.models import MtxDemo, MtxCategory, Post

admin.site.register(MtxDemo)

admin.site.register(MtxCategory)
admin.site.register(Post)