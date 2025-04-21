from user_management import UserManagement

def display_menu():
    print("\n=== Social Network Application ===")
    print("1. Register")
    print("2. Login")
    print("3. View Profile")
    print("4. Edit Profile")
    print("5. Exit")
    return input("Enter your choice (1-5): ").strip()

def main():
    user_manager = UserManagement()
    
    while True:
        choice = display_menu()
        
        if choice == "1":
            user_manager.register_user()
        elif choice == "2":
            user_manager.login()
        elif choice == "3":
            user_manager.view_profile()
        elif choice == "4":
            user_manager.edit_profile()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
