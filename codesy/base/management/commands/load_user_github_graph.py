from neo4j.v1 import GraphDatabase, basic_auth

from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import User
from gh_gql import user as github_user


def neo4j_merge_user(user, session):
    user_neo4j_rep = """
    (u:User {
        name: '%s', id: '%s', email: '%s'
    })
    """ % (user['name'], user['id'], user['email'])
    session.run("MERGE %s" % user_neo4j_rep)
    return user_neo4j_rep


def neo4j_merge_repo(repo, session):
    repo_neo4j_rep = (
        "(r:Repo {full_name: '%s'})" % repo['name']
    )
    session.run("MERGE %s" % repo_neo4j_rep)
    return repo_neo4j_rep


def neo4j_merge_repo_list(user, repos, repo_type, session):
    for repo in repos:
        repo_neo4j_rep = neo4j_merge_repo(repo, session)
        relationship = "MATCH (%s),(%s) CREATE (u)-[:%s]->(r)" % (
            user, repo_neo4j_rep, repo_type
        )
        session.run(relationship)


class Command(BaseCommand):
    def handle(self, *args, **options):
        driver = GraphDatabase.driver(settings.NEO4J_BOLT_URL, auth=basic_auth(
            settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        session = driver.session()

        # TODO: Figure out a way to not delete the whole graph db every time
        session.run("MATCH (n) DETACH DELETE n")
        test_users = ['aprilchomp', 'jdungan', 'jsatt', 'mrmakeit', 'jgmize',
                      'groovecoder']

        for username in test_users:
            gh_user = github_user.get(username)['user']
            neo4j_user = neo4j_merge_user(gh_user, session)
            neo4j_merge_repo_list(neo4j_user, gh_user['repositories'], 'OWNER' ,session)
            neo4j_merge_repo_list(neo4j_user, gh_user['starredRepositories'], 'STARRED', session)
            neo4j_merge_repo_list(neo4j_user, gh_user['contributedRepositories'], 'CONTRIBUTED', session)


        '''
        Recommend repos to a user: i.e., repos that have been starred the most by the users who share stars with this user:
            MATCH (user: User {username: username})-[:STARRED]->(r)<-[:STARRED]-(coStars),
                (coStars)->[:STARRED]->(r2)
            WHERE NOT (user)-[:STARRED]->(r2)
            RETURN r2.owner + r2.name AS Recommended, count(*) as Strength ORDER BY Strength DESC
        '''
