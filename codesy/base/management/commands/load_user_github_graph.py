from neo4j.v1 import GraphDatabase, basic_auth

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        driver = GraphDatabase.driver(settings.NEO4J_BOLT_URL, auth=basic_auth(
            settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        '''
        For each user:
            CREATE (username:User {username: username})
            GET https://api.github.com/users/%s/starred % user.username
            For each starred repo:
                CREATE (repo: Project {owner:owner, name:name})
                CREATE (username)-[:STARRED]->(repo)
            GET https://api.github.com/issues?filter=subscribed
            For each subscribed issue:
                CREATE (issue: Issue {url:rul})
                CREATE (issue)--(repo)
                CREATE (username)-[:SUBSCRIBED]->(issue)

        Recommend repos to a user: i.e., repos that have been starred the most by the users who share stars with this user:
            MATCH (user: User {username: username})-[:STARRED]->(r)<-[:STARRED]-(coStars),
                (coStars)->[:STARRED]->(r2)
            WHERE NOT (user)-[:STARRED]->(r2)
            RETURN r2.owner + r2.name AS Recommended, count(*) as Strength ORDER BY Strength DESC
        '''
