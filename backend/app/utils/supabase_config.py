# filepath: project/backend/app/utils/supabase_config.py

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """
    Creates and returns a Supabase client instance.
    
    Returns:
        Client: Supabase client instance
    """
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL and key must be set in environment variables")
    
    return create_client(supabase_url, supabase_key)

# Allow for direct testing of this module
if __name__ == "__main__":
    try:
        client = get_supabase_client()
        print("Supabase client created successfully")
    except Exception as e:
        print(f"Error creating Supabase client: {e}")