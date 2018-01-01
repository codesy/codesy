import logging

from neo4j.v1 import GraphDatabase, basic_auth

from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import User
from gh_gql import User as ghUser, RepoList

logging.basicConfig()

logger = logging.getLogger(__name__)


def neo4j_merge_user(user, session):
    # neo4j statement requires a name parameter; set if empty
    user.setdefault('name', '')
    statement = """
        MERGE (u:User {{id:'{}'}})
        SET u.name='{}', u.email='{}', u.login='{}'
    """.format(user['id'], user['name'], user['email'], user['login'])
    session.run(statement)
    session.sync()


def neo4j_merge_repo(repo, session):
    template = """
      MERGE (r:Repo {{id:'{}'}})
      SET r.name='{}', r.primaryLanguage='{}', r.owner='{}'
    """
    if 'primaryLanguage' in repo.keys():
        language = (
            repo['primaryLanguage']['name'] if repo['primaryLanguage'] else ""
        )
    else:
        language = u'none'
    statement = (
        template.format(repo['id'], repo['name'], language, repo['owner'])
    )
    session.run(statement)
    session.sync()


def neo4j_match_repo_relationship(user_id, repo_id, relationship, session):
    statement = """
       MATCH (u:User),(r:Repo) WHERE u.id ='{}' AND r.id='{}'
       CREATE (u)-[:{}]->(r)
    """.format(user_id, repo_id, relationship)
    session.run(statement)
    session.sync()


class Command(BaseCommand):
    def handle(self, *args, **options):
        driver = GraphDatabase.driver(settings.NEO4J_BOLT_URL, auth=basic_auth(
            settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        session = driver.session()

        # TODO: Figure out a way to not delete the whole graph db every time
        # session.run("MATCH (n) DETACH DELETE n")
        # FIXED by using MERGE/SET statements

        user_list = [
            user[0] for user in User.objects.all().values_list('username')
        ]

        # user_list = [
        #     'aprilchomp', 'jsatt', 'mrmakeit', 'jgmize', 'groovecoder'
        # ]

        repo_types = {
            'repositories': 'OWNER',
            'starredRepositories': 'STARRED',
            'contributedRepositories': "CONTRIBUTED"
        }
        for username in user_list:
            if username == u'admin':
                continue

            try:
                gh_user = ghUser.get(login=username)['user']
                neo4j_merge_user(gh_user, session)
                for repo_type in repo_types.keys():
                    repos = RepoList(type=repo_type, login=username)
                    for repo in repos:
                        repo_values = repo['node']
                        neo4j_merge_repo(repo_values, session)
                        neo4j_match_repo_relationship(
                            gh_user['id'], repo_values['id'],
                            repo_types[repo_type], session
                        )
            except Exception as e:
                logger.error("load_user_github_graph, error: %s" % e)

        session.close()


'''
Recommend repos to a user: i.e., repos that have been starred the most by
the users who share stars with this user:

MATCH (u:User)-[:STARRED]->(r)<-[:STARRED]-(u2:User),(u2)-[:STARRED]->(r2)
WHERE NOT (u)-[:STARRED]->(r2)
RETURN  r2.name AS Recommended, count(*) as Strength ORDER BY Strength DESC

Recommended by language
MATCH (u:User{name:"April"}),(r:Repo {primaryLanguage: "JavaScript" })
WHERE NOT (u)-[:CONTRIBUTED]->(r)
RETURN  r.name AS Recommended, count(*) as Strength ORDER BY Strength DESC

'''
