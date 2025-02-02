from typing import Any, Dict, List, Optional, TypeVar, Generic
from supabase import AsyncClient, create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

T = TypeVar('T')

class SupabaseInterface(Generic[T]):
    """
    A generic interface for Supabase CRUD operations.
    """
    
    def __init__(self, table_name: str):
        """
        Initialize Supabase client and set table name.
        
        Args:
            table_name (str): Name of the table to perform operations on
        """
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.client: AsyncClient = create_client(supabase_url, supabase_key)
        self.table_name = table_name

    async def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new record in the table.
        
        Args:
            data (Dict[str, Any]): Data to insert
            
        Returns:
            T: Created record
            
        Raises:
            Exception: If creation fails
        """
        try:
            # Ensure client is initialized
            if not self.client:
                raise ValueError("Supabase client not initialized")
                
            # Print debug information
            print(f"Creating record in table {self.table_name}")
            print(f"Data: {data}")
            
            # Execute insert
            response = self.client.table(self.table_name).insert(data).execute()
            
            if not response.data:
                raise ValueError("No data returned from insert operation")
                
            print(f"Created record successfully: {response.data[0]}")
            return response.data[0]
        except Exception as e:
            print(f"Error details: {e}")
            if hasattr(e, 'response'):
                print(f"Response error: {e.response}")
            raise Exception(f"Failed to create record: {str(e)}")

    async def read(self, id: str) -> Optional[T]:
        """
        Read a record by ID.
        
        Args:
            id (str): Record ID
            
        Returns:
            Optional[T]: Record if found, None otherwise
            
        Raises:
            Exception: If read fails
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("id", id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Failed to read record: {str(e)}")

    async def read_all(self, query: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        Read all records, optionally filtered by query.
        
        Args:
            query (Optional[Dict[str, Any]]): Query parameters
            
        Returns:
            List[T]: List of records
            
        Raises:
            Exception: If read fails
        """
        try:
            builder = self.client.table(self.table_name).select("*")
            if query:
                for key, value in query.items():
                    builder = builder.eq(key, value)
            response = builder.execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to read records: {str(e)}")

    async def update(self, id: str, data: Dict[str, Any]) -> T:
        """
        Update a record by ID.
        
        Args:
            id (str): Record ID
            data (Dict[str, Any]): Updated data
            
        Returns:
            T: Updated record
            
        Raises:
            Exception: If update fails
        """
        try:
            response = self.client.table(self.table_name).update(data).eq("id", id).execute()
            return response.data[0]
        except Exception as e:
            raise Exception(f"Failed to update record: {str(e)}")

    async def delete(self, id: str) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id (str): Record ID
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            Exception: If deletion fails
        """
        try:
            self.client.table(self.table_name).delete().eq("id", id).execute()
            return True
        except Exception as e:
            raise Exception(f"Failed to delete record: {str(e)}")

    async def upsert(self, data: Dict[str, Any], unique_columns: List[str]) -> T:
        """
        Insert or update a record based on unique columns.
        
        Args:
            data (Dict[str, Any]): Data to upsert
            unique_columns (List[str]): Columns that determine uniqueness
            
        Returns:
            T: Upserted record
            
        Raises:
            Exception: If upsert fails
        """
        try:
            response = self.client.table(self.table_name).upsert(data, on_conflict=",".join(unique_columns)).execute()
            return response.data[0]
        except Exception as e:
            raise Exception(f"Failed to upsert record: {str(e)}")

    async def batch_create(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """
        Create multiple records in a single operation.
        
        Args:
            data_list (List[Dict[str, Any]]): List of records to create
            
        Returns:
            List[T]: List of created records
            
        Raises:
            Exception: If batch creation fails
        """
        try:
            response = await self.client.table(self.table_name).insert(data_list).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to batch create records: {str(e)}")

    async def batch_update(self, updates: List[Dict[str, Any]], id_field: str = "id") -> List[T]:
        """
        Update multiple records in a single operation.
        
        Args:
            updates (List[Dict[str, Any]]): List of records with updates
            id_field (str): Name of the ID field
            
        Returns:
            List[T]: List of updated records
            
        Raises:
            Exception: If batch update fails
        """
        try:
            # Group updates by their IDs
            updates_by_id = {update[id_field]: update for update in updates}
            ids = list(updates_by_id.keys())
            
            # Perform batch update
            response = self.client.table(self.table_name)\
                .update([updates_by_id[id_] for id_ in ids])\
                .in_(id_field, ids)\
                .execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to batch update records: {str(e)}")
