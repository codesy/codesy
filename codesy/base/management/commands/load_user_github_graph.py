from neo4j.v1 import GraphDatabase, basic_auth
import requests

from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import User


STARRED_REPOS_URL = 'https://api.github.com/users/%s/starred'
SUBSCRIBED_REPOS_URL = 'https://api.github.com/users/%s/subscriptions'


def neo4j_merge_repo(repo, session):
    repo_neo4j_rep = (
        "(r:Repo {full_name: '%s'})" % repo.get('full_name')
    )
    session.run("MERGE %s" % repo_neo4j_rep)
    return repo_neo4j_rep


class Command(BaseCommand):
    def handle(self, *args, **options):
        driver = GraphDatabase.driver(settings.NEO4J_BOLT_URL, auth=basic_auth(
            settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        session = driver.session()
        # TODO: Figure out a way to not delete the whole graph db every time
        session.run("MATCH (n) DETACH DELETE n")
        test_users = ['groovecoder', 'jdungan', 'jsatt', 'mrmakeit', 'jgmize',
                      'aprilchomp']
        # for user in User.objects.values_list('username', flat=True):
        for username in test_users:
            user_neo4j_rep = "(u:User {username: '%s'})" % username
            session.run("CREATE %s" % user_neo4j_rep)

            user_starred_repos_url = STARRED_REPOS_URL % username
            resp = requests.get(user_starred_repos_url)

            if resp.status_code != 200:
                continue
            # TODO: handle API pagination
            for repo in resp.json():
                repo_neo4j_rep = neo4j_merge_repo(repo, session)

                relationship = "MATCH (%s),(%s) CREATE (u)-[:STARRED]->(r)" % (
                    user_neo4j_rep, repo_neo4j_rep
                )
                session.run(relationship)

            user_subscribed_repos_url = SUBSCRIBED_REPOS_URL % username
            resp = requests.get(user_subscribed_repos_url)

            if resp.status_code != 200:
                continue
            # TODO: handle API pagination
            for repo in resp.json():
                repo_neo4j_rep = neo4j_merge_repo(repo, session)

                relationship = "MATCH (%s),(%s) CREATE (u)-[:SUBSCRIBED]->(r)" % (
                    user_neo4j_rep, repo_neo4j_rep
                )
                session.run(relationship)

        '''
        Recommend repos to a user: i.e., repos that have been starred the most by the users who share stars with this user:
            MATCH (user: User {username: username})-[:STARRED]->(r)<-[:STARRED]-(coStars),
                (coStars)->[:STARRED]->(r2)
            WHERE NOT (user)-[:STARRED]->(r2)
            RETURN r2.owner + r2.name AS Recommended, count(*) as Strength ORDER BY Strength DESC
        '''
