from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import Question, Choice

class RequiredChoice(BaseInlineFormSet):
    
    def clean(self) -> None:
        """Check that at least one Choice has been entered"""
        super(RequiredChoice, self).clean()
        if any(self.errors):
            return
        if not any(cleaned_data and not cleaned_data.get('DELETE', False)
            for cleaned_data in self.cleaned_data):
            raise forms.ValidationError('At least one choice required.')

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    formset = RequiredChoice
    exclude = ["votes"]

class QuestionAdmin(admin.ModelAdmin):
    fields = ["pub_date", "question_text"]
    inlines = [ChoiceInline]
    list_display = ("id","question_text", "pub_date", "was_published_recently")
    list_filter = ["pub_date"]
    search_fields = ["question_text"]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)