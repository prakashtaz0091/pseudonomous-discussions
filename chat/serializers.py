from .models import DiscussionRoom
from rest_framework import serializers

class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiscussionRoom
        fields = '__all__'