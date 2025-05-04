
from rest_framework import serializers
from .models import Event, Project, ProjectMember, ProjectTask, StudentEvent

from users.models import User

class StudentSerializer(serializers.ModelSerializer):
    class_number = serializers.IntegerField(source='profile.class_number', read_only=True)
    class_letter = serializers.CharField(source='profile.class_letter', read_only=True)

    class Meta:
        model = User
        fields = [ 'full_name', 'avatar', 'class_number', 'class_letter' ]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = 'title date time'.split()


class ProjectTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTask
        fields = 'id title status'.split()

class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = 'id student role_in_project'.split()


class ProjectSerializer(serializers.ModelSerializer):
    all_tasks = ProjectTaskSerializer(many=True, read_only=True)
    active_tasks = ProjectTaskSerializer(many=True, read_only=True)
    members = ProjectMemberSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = 'project_code title start_date priority avatar all_tasks active_tasks members'.split()



class StudentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEvent
        fields = 'student title description'.split()