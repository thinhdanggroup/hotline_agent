# Supabase Interface

A generic interface for handling CRUD (Create, Read, Update, Delete) operations with Supabase in Python.

## Setup

1. Install required packages:
```bash
pip install supabase python-dotenv
```

2. Set up environment variables in `.env`:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Usage

### Basic Usage

```python
from supabase_interface import SupabaseInterface
from typing import TypedDict

# Define your data type
class User(TypedDict):
    id: str
    name: str
    email: str

# Initialize the interface
users_db = SupabaseInterface[User]("users")

# Create
new_user = await users_db.create({
    "name": "John Doe",
    "email": "john@example.com"
})

# Read
user = await users_db.read("user_id")

# Update
updated_user = await users_db.update("user_id", {
    "name": "John Smith"
})

# Delete
success = await users_db.delete("user_id")
```

### Advanced Features

1. Batch Operations:
```python
# Batch create
users = await users_db.batch_create([
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"}
])

# Batch update
updates = [
    {"id": "1", "name": "Alice Smith"},
    {"id": "2", "name": "Bob Johnson"}
]
updated_users = await users_db.batch_update(updates)
```

2. Upsert Operation:
```python
# Insert or update based on email
user = await users_db.upsert(
    {"email": "john@example.com", "name": "John Doe"},
    unique_columns=["email"]
)
```

3. Query Filtering:
```python
# Read with query
active_users = await users_db.read_all({
    "is_active": True,
    "role": "user"
})
```

## Error Handling

The interface includes built-in error handling for all operations. Errors are raised with descriptive messages:

```python
try:
    user = await users_db.read("invalid_id")
except Exception as e:
    print(f"Error: {str(e)}")
```

## Type Safety

The interface is generic and type-safe when used with TypedDict:

```python
from typing import TypedDict, Optional

class Product(TypedDict):
    id: str
    name: str
    price: float
    description: Optional[str]

products_db = SupabaseInterface[Product]("products")
```

This ensures type checking at development time and better code completion in IDEs.
