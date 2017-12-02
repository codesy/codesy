import requests

from django.conf import settings

GITHUB_ROOT = 'https://api.github.com/graphql'
GITHUB_API_KEY = settings.GITHUB_API_KEY
headers = {"Authorization": 'bearer %s' % GITHUB_API_KEY}


def gql_object(data):
    new_obj = {}
    for key in data.keys():
        if key == 'node':
            return gql_object(data[key])
        if isinstance(data[key], unicode):
            new_obj[key] = data[key]
        if isinstance(data[key], dict):
            new_obj[key] = gql_object(data[key])
        if isinstance(data[key], list):
            new_list = []
            for node in data[key]:
                new_list.append(gql_object(node))
            return new_list
    return new_obj


class GithubQuery(object):
    """generic graphql query. must supply query string"""
    def __init__(self, gql_query):
        self.query_string = gql_query

    def get(self, username):
        query_with_arg = {
            'query': self.query_string % username
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
                return gql_object(response['data'])
        else:
            raise Exception("""
                Query failed to run by returning code of {}. {}
            """.format(request.status_code, self.query_string))


user_info = """
query{
  user(login:"%s") {
    id
    name
    email
    starredRepositories(last:100){
      edges{
        node{
          id
          name
          primaryLanguage{
            id
            name
          }
          languages(first:5){
            edges{
                node{
                    name
                }
            }
          }
        }
      }
    }
    contributedRepositories (last:100) {
      edges {
        node {
          id
          name
          primaryLanguage{
            id
            name
          }
          languages (first:5) {
            edges {
              node {
                name
              }
            }
          }
        }
      }
    }
    repositories (last:100) {
      edges {
        node {
          id
          name
          primaryLanguage{
            id
            name
          }
          languages (first:5) {
            edges {
              node {
                name
              }
            }
          }
        }
      }
    }
  }
}
"""

user = GithubQuery(user_info)
