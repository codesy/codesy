from neo4j.v1 import GraphDatabase, basic_auth
from django.db import models
from django.conf import settings

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)

# Connect to NEO4J DB
driver = GraphDatabase.driver(settings.NEO4J_BOLT_URL, auth=basic_auth(
    settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)

session = driver.session()

# query template for repos starred by other codesy user_list
starred_template = """
MATCH (u:User)-[:STARRED]->(r)<-[:STARRED]-(u2:User),(u2)-[:STARRED]->(r2)
WHERE NOT (u)-[:STARRED]->(r2)
RETURN  r2.name AS Recommended, count(*) as Strength ORDER BY Strength DESC
ORDER BY title ASC LIMIT 10;
"""


class Starred(models.Model):

    def __init__(self):
        results = session.run(starred_template)
        import ipdb; ipdb.set_trace()
        return results
