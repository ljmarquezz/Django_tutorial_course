from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import Question, Choice

class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 3
    exclude = ["votes"]

class QuestionAdmin(admin.ModelAdmin):
    fields = ["pub_date", "question_text"]
    inlines = [ChoiceInline]
    list_display = ("id","question_text", "pub_date", "was_published_recently")
    list_filter = ["pub_date"]
    search_fields = ["question_text"]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)