from supabase_interface import SupabaseInterface
from typing import TypedDict, Optional
from datetime import datetime

# Define a type for your data
class User(TypedDict):
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime]

async def main():
    # Initialize the interface with your table name
    users_db = SupabaseInterface[User]("users")
    
    # Example: Create a new user
    new_user = {
        "name": "John Doe",
        "email": "john@example.com",
        "created_at": datetime.now()
    }
    
    try:
        # Create a user
        user = await users_db.create(new_user)
        print(f"Created user: {user}")
        
        # Read the user
        user_id = user["id"]
        retrieved_user = await users_db.read(user_id)
        print(f"Retrieved user: {retrieved_user}")
        
        # Update the user
        updated_data = {
            "name": "John Smith",
            "updated_at": datetime.now()
        }
        updated_user = await users_db.update(user_id, updated_data)
        print(f"Updated user: {updated_user}")
        
        # Read all users
        all_users = await users_db.read_all()
        print(f"All users: {all_users}")
        
        # Delete the user
        deleted = await users_db.delete(user_id)
        print(f"User deleted: {deleted}")
        
        # Batch operations example
        users_to_create = [
            {
                "name": "Alice Smith",
                "email": "alice@example.com",
                "created_at": datetime.now()
            },
            {
                "name": "Bob Johnson",
                "email": "bob@example.com",
                "created_at": datetime.now()
            }
        ]
        
        created_users = await users_db.batch_create(users_to_create)
        print(f"Batch created users: {created_users}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
