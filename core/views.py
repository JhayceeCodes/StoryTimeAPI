from django.shortcuts import render
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', block=True)
def home(request):
    return HttpResponse("Hello, world!")
