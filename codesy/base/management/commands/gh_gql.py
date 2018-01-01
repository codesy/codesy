import requests

from django.conf import settings

GITHUB_ROOT = 'https://api.github.com/graphql'
GITHUB_API_KEY = settings.GITHUB_API_KEY
headers = {"Authorization": 'bearer %s' % GITHUB_API_KEY}


class ghQuery(object):
    """generic graphql query. must supply query string"""
    def __init__(self, query_string):
        self.template = query_string
        self.response_dict = {}

    def get(self, **kwargs):
        query_with_arg = {
            'query': self.template,
            'variables': kwargs
        }
        request = requests.post(
            GITHUB_ROOT, json=query_with_arg, headers=headers)
        if request.status_code == 200:
            response = request.json()
            if 'errors' in response.keys():
                for error in response['errors']:
                    raise Exception("""
                        Error: {} At: {}
                    """.format(error['message'], error['locations'])
                    )
            else:
                return response['data']
        else:
            raise Exception("""
                Query failed to run by returning code of {}. {}
            """.format(request.status_code, self.query_string))


class RepoList(object):
    """returns a iterator of repos."""
    def __init__(self, **kwargs):
        self.type = kwargs['type']
        self.gh_query = ghQuery(repo_query % self.type)
        self.repositories = []
        self.kwargs = kwargs
        self.request()

    def __iter__(self):
        for r in self.repositories:
            yield r
        if self.hasNextPage:
            self.request()
            for r in self.__iter__():
                yield r

    def request(self):
        self.response = self.gh_query.get(**self.kwargs)
        list_info = self.response['user'][self.type]
        self.repositories = list_info['edges']
        self.hasNextPage = list_info['pageInfo']['hasNextPage']
        self.kwargs['after'] = list_info['pageInfo']['endCursor']


user_query = """
query UserRepos ($login: String!){
  user(login: $login) {
    id
    name
    email
    login
    avatarUrl
    }
}
"""

repo_query = """
query UserRepos($login: String!, $after: String) {
  user(login: $login) {
    login
    %s(first: 100, after: $after) {
        pageInfo{
            endCursor
            hasNextPage
        }
      edges {
        node {
          id
          owner
          name
          primaryLanguage {
            id
            name
          }
          languages(first: 100) {
            edges {
              node {
                name
                id
              }
            }
          }
        }
      }
    }
  }
}
"""

User = ghQuery(user_query)

issue_query = """
query findIssue($url: URI!) {
  resource(url: $url) {
    __typename
    ... on Issue {
      state
    }

  }
}
"""

Issue = ghQuery(issue_query)
