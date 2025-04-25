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
        self.execute_query(query, {'username': username})