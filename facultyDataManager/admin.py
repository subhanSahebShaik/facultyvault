from django.contrib import admin
from .models import Faculty, BookPublication, Certification, ConferencePublication, JournalPublication, Patent

# Register your models here.
admin.site.register(Faculty)
admin.site.register(BookPublication)
admin.site.register(Certification)
admin.site.register(ConferencePublication)
admin.site.register(JournalPublication)
admin.site.register(Patent)