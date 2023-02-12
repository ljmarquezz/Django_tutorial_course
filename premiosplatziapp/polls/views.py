from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Question, Choice
from django.views import generic


#esta es una function based view
# def index(request):
#     latest_question_list = Question.objects.all()
#     return render(request, "polls/index.html", {
#         "latest_question_list": latest_question_list
#     })

"""Misma vista pero con Generic Views"""
class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions"""
        #ordenadas desde la mas reciente hasta la mas antigua
        return Question.objects.order_by("-pub_date")[:5] 

#esta es una function based view
# def detail(request, question_id):
#     q = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {
#         'question': q
#     })

"""Misma vista pero con Generic Views"""
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

#esta es una function based view
# def results(request, question_id):
#     q = get_object_or_404(Question, pk=question_id)
#     return render(request, "polls/results.html", {
#         "question": q
#     })

"""Misma vista pero con Generic Views"""
class ResultView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(request, "polls/detail.html", {
            "question": question,
            "error_message": "No elegiste una respuesta"
        })
    else: 
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
