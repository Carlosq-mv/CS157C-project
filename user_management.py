from database import Database
import getpass
import re

class UserManagement:
    def __init__(self):
        self.db = Database()
        self.current_user = None
        
    def __del__(self):
        self.db.close()
        
    def register_user(self):
        print("\n=== User Registration ===")
        name = input("Enter your full name: ").strip()
        email = input("Enter your email: ").strip()
        username = input("Enter your username: ").strip()
        password = getpass.getpass("Enter your password: ").strip()
        
        # Basic validation
        if not all([name, email, username, password]):
            print("Error: All fields are required!")
            return False
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("Error: Invalid email format!")
            return False
            
        # Check if username already exists
        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            print("Error: Username already exists!")
            return False
            
        # Create user
        result = self.db.create_user(username, email, password, name)
        if result:
            print("Registration successful!")
            return True
        else:
            print("Error: Registration failed!")
            return False
            
    def login(self):
        print("\n=== User Login ===")
        username = input("Enter your username: ").strip()
        password = getpass.getpass("Enter your password: ").strip()
        
        user = self.db.get_user_by_username(username)
        if not user:
            print("Error: User not found!")
            return False
            
        if user[0]['u']['password'] != password:
            print("Error: Invalid password!")
            return False
            
        self.current_user = user[0]['u']
        print(f"Welcome back, {self.current_user['name']}!")
        return True
        
    def view_profile(self):
        if not self.current_user:
            print("Error: Please login first!")
            return
            
        print("\n=== Your Profile ===")
        print(f"Name: {self.current_user['name']}")
        print(f"Username: {self.current_user['username']}")
        print(f"Email: {self.current_user['email']}")
        print(f"Bio: {self.current_user['bio']}")
        
    def edit_profile(self):
        if not self.current_user:
            print("Error: Please login first!")
            return
            
        print("\n=== Edit Profile ===")
        print("Leave blank to keep current value")
        
        name = input(f"Name [{self.current_user['name']}]: ").strip()
        email = input(f"Email [{self.current_user['email']}]: ").strip()
        bio = input(f"Bio [{self.current_user['bio']}]: ").strip()
        
        # Validate email if provided
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("Error: Invalid email format!")
            return
            
        # Update user
        result = self.db.update_user(
            self.current_user['username'],
            name=name or None,
            email=email or None,
            bio=bio or None
        )
        
        if result:
            print("Profile updated successfully!")
            # Refresh current user data
            self.current_user = self.db.get_user_by_username(self.current_user['username'])[0]['u']
        else:
            print("Error: Failed to update profile!") 