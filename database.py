from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
        
    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return result.data()

    def create_user(self, username, email, password, name):
        query = """
        CREATE (u:User {
            username: $username,
            email: $email,
            password: $password,
            name: $name,
            bio: '',
            created_at: datetime()
        })
        RETURN u
        """
        return self.execute_query(query, {
            'username': username,
            'email': email,
            'password': password,
            'name': name
        })

    def get_user_by_username(self, username):
        query = """
        MATCH (u:User {username: $username})
        RETURN u
        """
        return self.execute_query(query, {'username': username})

    def update_user(self, username, **kwargs):
        set_clauses = []
        parameters = {'username': username}
        
        for key, value in kwargs.items():
            if value is not None:
                set_clauses.append(f"u.{key} = ${key}")
                parameters[key] = value
                
        if not set_clauses:
            return None
            
        query = f"""
        MATCH (u:User {{username: $username}})
        SET {', '.join(set_clauses)}
        RETURN u
        """
        return self.execute_query(query, parameters)
    
    def follow_user(self, follower_username, followee_username):
        if follower_username == followee_username:
            print("You cannot follow yourself.")
            return

        check_users_query = """
        MATCH (a:User {username: $follower_username}), (b:User {username: $followee_username})
        RETURN COUNT(a) > 0 AS follower_exists, COUNT(b) > 0 AS followee_exists
        """
        result = self.execute_query(check_users_query, {
            'follower_username': follower_username,
            'followee_username': followee_username
        })

        if not result or not result[0]['follower_exists'] or not result[0]['followee_exists']:
            print("One or both users do not exist.")
            return

        rel_check_query = """
        MATCH (a:User {username: $follower_username})-[r:FOLLOWS]->(b:User {username: $followee_username})
        RETURN COUNT(r) AS rel_count
        """
        rel_result = self.execute_query(rel_check_query, {
            'follower_username': follower_username,
            'followee_username': followee_username
        })

        if rel_result[0]['rel_count'] > 0:
            print("You already follow this user.")
            return

        create_query = """
        MATCH (a:User {username: $follower_username}), (b:User {username: $followee_username})
        MERGE (a)-[:FOLLOWS]->(b)
        """
        self.execute_query(create_query, {
            'follower_username': follower_username,
            'followee_username': followee_username
        })

        print(f"You are now following @{followee_username}.")

    def unfollow_user(self, follower_username, followee_username):
        if follower_username == followee_username:
            print("You cannot unfollow yourself.")
            return

        check_users_query = """
        MATCH (a:User {username: $follower_username}), (b:User {username: $followee_username})
        RETURN COUNT(a) > 0 AS follower_exists, COUNT(b) > 0 AS followee_exists
        """
        result = self.execute_query(check_users_query, {
            'follower_username': follower_username,
            'followee_username': followee_username
        })

        if not result or not result[0]['follower_exists'] or not result[0]['followee_exists']:
            print("One user do not exist.")
            return

        check_relationship_query = """
        MATCH (a:User {username: $follower_username})-[r:FOLLOWS]->(b:User {username: $followee_username})
        RETURN COUNT(r) AS rel_count
        """
        rel_result = self.execute_query(check_relationship_query, {
            'follower_username': follower_username,
            'followee_username': followee_username
        })

        if rel_result[0]['rel_count'] == 0:
            print("You are not following this user.")
            return

        delete_query = """
        MATCH (a:User {username: $follower_username})-[r:FOLLOWS]->(b:User {username: $followee_username})
        DELETE r
        """
        self.execute_query(delete_query, {
            'follower_username': follower_username,
            'followee_username': followee_username
        })

        print(f"You have unfollowed @{followee_username}.")

    def get_connections_combined(self, username):
        query = """
        MATCH (u:User {username: $username})
        OPTIONAL MATCH (follower:User)-[:FOLLOWS]->(u)
        WITH u, COLLECT({username: follower.username, name: follower.name}) AS followers
        OPTIONAL MATCH (u)-[:FOLLOWS]->(followee:User)
        WITH followers, COLLECT({username: followee.username, name: followee.name}) AS following
        RETURN followers, following
        """
        result = self.execute_query(query, {'username': username})
        return result[0] if result else {'followers': [], 'following': []}

    def get_mutual_friends(self, username1, username2):
        query = """
        MATCH (a:User {username: $username1})-[:FOLLOWS]->(x:User)<-[:FOLLOWS]-(b:User {username: $username2})
        RETURN x.username AS username, x.name AS name
        """
        return self.execute_query(query, {'username1': username1, 'username2': username2})

    def search_user(self, query_item):
        query = """
        MATCH (u:User)
        WHERE toLower(u.username) CONTAINS toLower($query_item) 
        OR toLower(u.name) CONTAINS toLower($query_item)
        RETURN u
        """
        return self.execute_query(query, {'query_item': query_item})

    def most_followed(self, limit):
        query = """
        MATCH (f:User)<-[:FOLLOWS]-(u:User)
        WITH f.username AS username, f.name AS name, COUNT(u) AS follower_count
        RETURN name, username, follower_count
        ORDER BY follower_count DESC
        LIMIT $limit
        """
        return self.execute_query(query, {'limit': limit})

    def recommendations(self, username):
        query = """
        MATCH (u:User {username: $username})-[:FOLLOWS]->(friend:User)-[:FOLLOWS]->(recommended:User)
        WHERE NOT (u)-[:FOLLOWS]->(recommended) AND u <> recommended
        RETURN recommended.username AS username, recommended.name AS name, COUNT(friend) AS mutual_friends
        ORDER BY mutual_friends DESC
        LIMIT 10
        """
        return self.execute_query(query, {'username': username})
