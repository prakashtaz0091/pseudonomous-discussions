# chat/views.py
from django.shortcuts import render
from . import models

def index(request):
    return render(request, "chat/index.html")



# def room(request, room_name):
def room(request):
    room_name = request.GET.get("room_name", None)
    room = models.DiscussionRoom.objects.get(name=room_name)
    return render(request, "chat/room.html",{"room": room})