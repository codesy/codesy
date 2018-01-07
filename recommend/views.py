from django.views.generic import TemplateView
from models import Starred


class RecommendRepoView(TemplateView):
    template_name = 'repo_list.html'

    def get_context_data(self, **kwargs):
        stars = Starred()

        return dict({'recommendations': []})
