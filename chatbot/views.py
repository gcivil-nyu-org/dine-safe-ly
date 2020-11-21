from django.shortcuts import render

def chatbot(request):
    return render(
        request=request, template_name="chat2.html"
    )