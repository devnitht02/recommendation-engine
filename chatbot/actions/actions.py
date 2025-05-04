# actions.py
import django
import sys
import os

# 1. Bootstrap Django
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../')))
sys.path.append("C:/Users/devni/Documents/Steps-Internship-Recommendation/recommender")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recommender.settings")

import django

django.setup()

from rasa_sdk import Action
from rasa_sdk.knowledge_base.storage import KnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase

# 2. Import your real models
from institutions.models import WnInstitution, WnCourse


class DjangoKnowledgeBase(KnowledgeBase):
    async def get_object_types(self, session_id):
        # expose two types for the KB
        return ["course", "institution"]

    async def get_objects(self, session_id, object_type, query=None, limit=None):
        """
        Called when Rasa needs a list of objects
        (e.g. “list some courses” or autocomplete suggestions).
        """
        if object_type == "course":
            qs = WnCourse.objects.all()
            # filter on your course_name field
            if query:
                qs = qs.filter(course_name__icontains=query)
            if limit:
                qs = qs[:limit]
            return [{"id": c.id, "name": c.course_name} for c in qs]

        # institution branch
        qs = WnInstitution.objects.all()
        if query:
            qs = qs.filter(institution_name__icontains=query)
        if limit:
            qs = qs[:limit]
        return [{"id": i.id, "name": i.institution_name} for i in qs]

    async def get_object(self, session_id, object_type, object_id):
        """
        Fetch the single object’s full data when the user selects it.
        """
        if object_type == "course":
            try:
                c = WnCourse.objects.get(id=object_id)
            except WnCourse.DoesNotExist:
                return {}
            return {
                "id": c.id,
                "name": c.course_name,
                "description": c.course_description,
                "duration_years": c.duration_years,
                "rank": c.rank,
                "degree_price": c.degree_price,
                # you could add stream and degree names too:
                "stream": c.stream.stream_name if c.stream else "",
                "degree": c.degree.degree_name if c.degree else "",
            }

        # institution branch
        try:
            inst = WnInstitution.objects.get(id=object_id)
        except WnInstitution.DoesNotExist:
            return {}
        return {
            "id": inst.id,
            "name": inst.institution_name,
            "website": inst.website or "",
            "type": inst.institution_type.type if inst.institution_type else "",
            "state": inst.state.name if hasattr(inst.state, "name") else str(inst.state),
            "district": inst.district.name if hasattr(inst.district, "name") else str(inst.district),
            "rank": inst.rank,
        }

    async def get_attributes_of_object(self, session_id, object_type, object_id):
        """
        Rasa will ask for a specific attribute
        (e.g. “what’s the description?” or “what’s the rank?”).
        Return the dict you made above so it can pluck out the right key.
        """
        return await self.get_object(session_id, object_type, object_id)


class ActionDjangoKnowledgeBase(ActionQueryKnowledgeBase):
    def __init__(self):
        # hand your ORM-backed KB to the built-in KB action
        super().__init__(DjangoKnowledgeBase())

    def name(self) -> str:
        # this name must match domain.yml’s action list
        return "action_query_knowledge_base"
