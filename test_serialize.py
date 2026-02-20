import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limefolio.settings')
django.setup()
from projects.models import Project
from projects.serializers import ProjectDetailSerializer
project = Project.objects.first()
if project:
    print(ProjectDetailSerializer(project).data.get('media'))
else:
    print("No project found")
