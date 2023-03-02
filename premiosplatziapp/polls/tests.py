import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls.base import reverse

from .models import Question, Choice

def create_question(question_text, days) -> Question:
    """
    Create a question with the given "question_text", and published with the given 
    number of days offset to now (negative for questions published in the past, and
    positive for questions published in the future)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text = question_text, pub_date = time)

def create_choice(question, choice_text):
    "Create a choice with the given choice text for the diven question"
    question.choice_set.create(choice_text = choice_text)
    return question

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
        future_question = create_choice(future_question, "1")
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, future_question.question_text)
        self.assertNotIn(future_question.question_text, response.context["latest_question_list"])
        future_question.delete()

    def test_past_questions(self):
        """Only questions published in the past should be displayed on the index view"""
        past_question = create_question("Probe", days=-30)
        past_question = create_choice(past_question, "1")
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)
        self.assertQuerysetEqual(response.context["latest_question_list"], [past_question])
        past_question.delete()
    
    def test_future_and_past_questions(self):
        """Even if both, past and future questions exist, only past questions are displayed"""
        future_question = create_question("Future", days=30)
        future_question = create_choice(future_question, "1")
        past_question = create_question("Past", days=-30)
        past_question = create_choice(past_question, "1")
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)
        self.assertNotContains(response, future_question.question_text)
        self.assertNotIn(future_question.question_text, response.context["latest_question_list"])
        self.assertQuerysetEqual(response.context["latest_question_list"], [past_question])
        future_question.delete()
        past_question.delete()
    
    def test_two_past_questions(self):
        """The questions index page may display multiple questions"""
        past_question1 = create_question("Past 1", days=-30)
        past_question2 = create_question("Past 2", days=-20)
        past_question1 = create_choice(past_question1, "1")
        past_question2 = create_choice(past_question2, "1")
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["latest_question_list"], [past_question2, past_question1])
        past_question1.delete()
        past_question2.delete()
    
    def test_two_future_questions(self):
        "Even if multiple future questions exist, none should be displayed"
        future_question1 = create_question("Future 1", days=30)
        future_question2 = create_question("Future 2", days=20)
        future_question1 = create_choice(future_question1, "1")
        future_question2 = create_choice(future_question2, "1")
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])
        future_question1.delete()
        future_question2.delete()
    
    def test_questions_without_choices(self):
        """Questions without choices shouldn't be displayed on the index view"""
        question_no_choices = create_question("No choices", -1)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])
        question_no_choices.delete()

    def test_only_questions_with_choices(self):
        """Only questions with choices are displayed on the index view"""
        question_no_choices = create_question("No choices", -1)
        question_w_choices = create_question("With choices", -1)
        question_w_choices = create_choice(question_w_choices, "c1")
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question_w_choices.question_text)
        self.assertNotContains(response, question_no_choices.question_text)
        self.assertNotIn(question_no_choices.question_text, response.context["latest_question_list"])
        self.assertQuerysetEqual(response.context["latest_question_list"], [question_w_choices])
        question_no_choices.delete()
        question_w_choices.delete()

class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 error not found
        """
        future_question = create_question("Future", days=30)
        future_question = create_choice(future_question, "1")
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        future_question.delete()

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question text and choices 
        """
        past_question = create_question("Past", days=-30)
        past_question = create_choice(past_question, "1")
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)
        past_question.delete()

class QuestionResultViewTests(TestCase):

    def test_future_question(self):
        """
        The result view of a question with a pub_date in the future
        returns a 404 error not found
        """
        future_question = create_question("Future", days=30)
        future_question = create_choice(future_question, "1")
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        future_question.delete()

    def test_past_question(self):
        """
        The result view of a question with a pub_date in the past
        displays the question text and votes
        """
        past_question = create_question("Past", days=-30)
        past_question = create_choice(past_question, "1")
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)
        past_question.delete()