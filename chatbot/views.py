from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def chatbot(request):
    return render(request=request, template_name="chat.html")
