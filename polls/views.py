"""Polls app views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views import View, generic

from user_profile import mixins as user_mixins

from . import mixins, models


class CreateQuestionView(mixins.TeacherRequiredMixin, generic.CreateView):
    """View to create question."""

    model = models.Question
    fields = ["question_text"]
    success_url = reverse_lazy("polls:question-list")
    template_name = "generic_create_update_form.html"
    extra_context = {"title_text": "Add Question", "button_text": "Add"}

    def form_valid(self, form: object) -> object:
        """For valid form submission.

        - Set the published date as the current date and time.
        - Set the author as the current logged in user.

        """
        form.instance.pub_date = now()
        form.instance.author = self.request.user
        return super().form_valid(form)


class UpdateQuestionView(mixins.TeacherAuthorRequiredMixin, generic.UpdateView):
    """View to update question."""

    model = models.Question
    fields = ["question_text", "pub_date"]
    success_url = reverse_lazy("polls:question-list")
    template_name = "generic_create_update_form.html"
    extra_context = {"title_text": "Edit Question", "button_text": "Update"}


class DeleteQuestionView(mixins.TeacherAuthorRequiredMixin, generic.DeleteView):
    """View to delete question."""

    model = models.Question
    success_url = reverse_lazy("polls:question-list")
    template_name = "generic_delete_confirm_form.html"
    extra_context = {"title_text": "Delete Question"}


class QuestionListView(generic.ListView):
    """Question List view of polls app.

    Default `template_name` if not specified is "polls/question_list.html"

    """

    model = models.Question
    queryset = models.Question.objects.order_by("-pub_date")[:5]


class QuestionDetailView(LoginRequiredMixin, generic.DetailView):
    """Detail view of polls app.

    Default `template_name` if not specified is "polls/question_detail.html"

    """

    model = models.Question


class CreateChoiceView(user_mixins.TeacherRequiredMixin, generic.CreateView):
    """View to create choice."""

    model = models.Choice
    fields = ["choice_text"]
    template_name = "generic_create_update_form.html"
    extra_context = {"title_text": "Add Choice", "button_text": "Add"}

    def get_success_url(self) -> object:
        """Overwrite the `success_url` to generate a dynamic URL.

        - Get the `pk` from the URLs to get the `question_id`.
        - Redirect to the question detail view of the question to which choice being added.

        """
        question_id = self.kwargs["pk"]
        return reverse_lazy("polls:question-detail", kwargs={"pk": question_id})

    def form_valid(self, form: object) -> object:
        """If the form data is valid, add current time as `pub_date`.

        - Set the `question` field (ForeignKey) of `Choice` model.
        - Get the `pk` from the URLs to get the `question_id`.

        """
        form.instance.question_id = self.kwargs["pk"]
        return super().form_valid(form)


class ResultsView(LoginRequiredMixin, generic.DetailView):
    """Results view of polls app."""

    model = models.Question
    template_name = "polls/results.html"


class SubmitVote(user_mixins.StudentRequiredMixin, View):
    """Vote View."""

    def post(self, request: object, question_id: int) -> object:
        """Vote counter function.

        - Set the `answered_by` for the `question` and `choice` objects as the current user.
        - Increment the `votes` for the `choice` by one.

        """
        question = get_object_or_404(models.Question, pk=question_id)
        try:
            question.answered_by.add(self.request.user)
            selected_choice = question.choice_set.get(pk=request.POST["choice"])
            selected_choice.answered_choice.add(self.request.user)
            selected_choice.votes += 1
            selected_choice.save()
            question.save()
        except (KeyError, models.Choice.DoesNotExist):
            context = {
                "question": question,
                "error_message": "You didn't select a choice.",
            }
            return render(request, "polls/details.html", context)
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
