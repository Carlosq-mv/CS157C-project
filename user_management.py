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

    def most_followed_profiles(self):
        if not self.current_user:
            print("Error: Please login first!")
            return

        print("\n=== Most Followed Users ===") 
        limit = input("Enter the number of top followed users you want to view (Max 20): ").strip()

        try:
            limit = int(limit)
            if limit > 20:
                print("You can only view a maximum of 20 users. Setting limit to 20.")
                limit = 20
            elif limit < 1:
                print("Please enter a number greater than 0")
                return
        except ValueError:
            print("Invalid type. Please enter a valid integer")
            return

        print("loading...") 
        users = self.db.most_followed(limit)

        if not users:
            print(f"No users are in the database at the momemt")
        else:
            print(f"\n=== Top {limit} Most Followed Users ===")  
            for user in users:
                print(f"Name: {user["name"]}")
                print(f"Username: {user["username"]}")
                print(f"Followers: {user["follower_count"]}")
                print("-" * 25) 

    def search_profile(self):
        if not self.current_user:
            print("Error: Please login first!")
            return

        print("\n=== Search User ===")
        print("Enter the name or username of the user you're looking for.")
        search_query = input("Name or Username (substring allowed): ").strip()

        print("loading...") 
        users = self.db.search_user(search_query)

        print("\n=== Results ===")  
        if not users:
            print(f"No user found with the name or username '{search_query}'")
        else:
            for user in users:
                u = user["u"]
                print(f"Name: {u["name"]}")
                print(f"Username: {u["username"]}")
                print(f"Bio: {u["bio"] if u["bio"] else "N/A"}")
                print("-" * 100)

    def recommended_profiles(self):
        if not self.current_user:
            print("Error: Please login first!")
            return

        print("\n=== Recommended Profiles To Follow ===")
        print(self.current_user['username'])
        users = self.db.recommendations(self.current_user["username"])
        if not users:
            print("No recommendations available at the moment.")
            return

        for user in users:
            print(f"Name: {user["name"]}")
            print(f"Username: {user["username"]}")
            print("-" * 25)