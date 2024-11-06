from django.urls import path
from .views import SendEmailView, FetchEmailsView, send_answer

urlpatterns = [
    path('send-email/', SendEmailView.as_view(), name='send_email'),
    path('fetch-emails/', FetchEmailsView.as_view(), name='fetch_emails'),
    path("send-answer/", send_answer, name="send_answer"),
]