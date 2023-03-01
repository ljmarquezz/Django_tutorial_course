import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls.base import reverse

from .models import Question

def create_question(question_text, days) -> Question:
    """
    Create a question with the given "question_text", and published with the given 
    number of days offset to now (negative for questions published in the past, and
    positive for questions published in the future)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text = question_text, pub_date = time)

#Normalmente se testean modelos o vistas

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_questions(self):
        """was_published_recently must return False for questions whose pub_date is in the future"""
        future_question = create_question("Probe", 30)
        self.assertIs(future_question.was_published_recently(), False)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """If no questions exist, an appropiate message is displayed"""
        response =  self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])
    
    def test_future_questions(self):
        """If future questions exist in the database, they are not displayed on the index view"""
        future_question = create_question("Probe", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, future_question.question_text)
        self.assertNotIn(future_question.question_text, response.context["latest_question_list"])
        future_question.delete()

    def test_past_questions(self):
        """Only questions published in the past should be displayed on the index view"""
        past_question = create_question("Probe", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)
        self.assertQuerysetEqual(response.context["latest_question_list"], [past_question])
        past_question.delete()