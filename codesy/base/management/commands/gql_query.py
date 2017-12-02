import re
import json
query = """
{
  user(login: "jgmize") {
    id
    name
    email
    starredRepositories(first: 3) {
      pageInfo {
        endCursor
        hasNextPage
        hasPreviousPage
        startCursor
      }
      edges {
        node {
          id
        }
      }
    }
  }
}
"""

result = '''
{
  "data": {
    "user": {
      "id": "MDQ6VXNlcjE2MTcxOA==",
      "name": "Josh Mize",
      "email": "",
      "starredRepositories": {
        "pageInfo": {
          "endCursor": "Y3Vyc29yOnYyOpHOADtrcw==",
          "hasNextPage": true,
          "hasPreviousPage": false,
          "startCursor": "Y3Vyc29yOnYyOpHOADtrcQ=="
        },
        "edges": [
          {
            "node": {
              "id": "MDEwOlJlcG9zaXRvcnkxMTc1NDk="
            }
          },
          {
            "node": {
              "id": "MDEwOlJlcG9zaXRvcnkxMTc3NDE="
            }
          },
          {
            "node": {
              "id": "MDEwOlJlcG9zaXRvcnkxMzg2MzU="
            }
          }
        ]
      }
    }
  }
}
'''


# ['data']['user']['starredRepositories']['pageInfo']['endCursor']

edges_re = re.compile('(\w+).*\(.*first.*\)')

edges = re.findall(edges_re, query)


for edge in edges:
    property_template = "%s[\S\s]*%s.+:(.*)?[,\}\n]"
    nextPage_re = re.compile(property_template % (edge,"hasNextPage"))
    endCursor_re = re.compile(property_template % (edge,"endCursor"))

    hasNextPage = re.findall(nextPage_re,result)[0]
    import ipdb; ipdb.set_trace()

    if hasNextPage == 'true':
            endCursor = re.findall(endCursor_re, result)[0]

print "edge:{}".format(edge)
print "hasNextPage:{}".format(hasNextPage)
print "endCursor:{}".format(endCursor)
