import os
from dotenv import load_dotenv
import requests

load_dotenv()

DAILY_API_KEY = os.environ.get("DAILY_API_KEY")
DAILY_API_URL = "https://api.daily.co/v1"

headers = {
    "Authorization": f"Bearer {DAILY_API_KEY}",
    "Content-Type": "application/json"
}

def get_all_rooms():
    """Retrieve all rooms from your Daily.co account with pagination handling."""
    rooms = []
    next_page = None
    
    while True:
        params = {'page': next_page} if next_page is not None else {}
        response = requests.get(
            f"{DAILY_API_URL}/rooms",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        rooms.extend(data['data'])
        next_page = data.get('next_page')
        
        if not next_page:
            break  # Exit loop when no more pages
    
    return rooms

def delete_all_rooms():
    """Delete all rooms in your Daily.co account."""
    rooms = get_all_rooms()
    
    if not rooms:
        print("No rooms found to delete.")
        return
    
    print(f"Found {len(rooms)} rooms to delete...")
    for room in rooms:
        room_name = room['name']
        try:
            response = requests.delete(
                f"{DAILY_API_URL}/rooms/{room_name}",
                headers=headers
            )
            response.raise_for_status()
            print(f"Successfully deleted room: {room_name}")
        except requests.exceptions.HTTPError as e:
            print(f"Failed to delete room {room_name}: {str(e)}")

if __name__ == "__main__":
    # Get and display all rooms first
    print("Fetching all rooms...")
    rooms = get_all_rooms()
    
    if not rooms:
        print("No rooms found.")
        exit()
        
    print("\nRooms in your account:")
    for idx, room in enumerate(rooms, 1):
        print(f"{idx}. {room['name']}")
    
    delete_all_rooms()