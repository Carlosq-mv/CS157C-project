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