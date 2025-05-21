import streamlit as st
import requests
import os
from dotenv import load_dotenv
from urllib.parse import quote
import time

# Load environment variables
load_dotenv()

def geocode_address(address):
    """
    Convert address to latitude and longitude coordinates using OpenStreetMap Nominatim
    
    Args:
        address (str): The address to geocode
        
    Returns:
        tuple: (latitude, longitude, status) where status is True if geocoding was successful
    """
    try:
        print(f"\nAttempting to geocode address: {address}")
        
        # Use OpenStreetMap Nominatim API
        print(f"Using OpenStreetMap Nominatim for geocoding")
        encoded_address = quote(address)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1"
        
        # Add a User-Agent header as required by Nominatim's usage policy
        headers = {
            'User-Agent': 'HungerHeal/1.0 (https://github.com/yourusername/hungerheal; your@email.com)'
        }
        
        print(f"Request URL: {url}")
        response = requests.get(url, headers=headers)
        print(f"Response status code: {response.status_code}")
        
        # Respect Nominatim's usage policy (1 request per second)
        time.sleep(1)
        
        data = response.json()
        
        if data and len(data) > 0:
            location = data[0]
            lat = float(location['lat'])
            lon = float(location['lon'])
            print(f"Successfully geocoded to: {lat}, {lon}")
            return lat, lon, True
        else:
            print(f"Geocoding error: No results found")
            print(f"Full response: {data}")
            return None, None, False
            
    except Exception as e:
        print(f"Geocoding error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None, None, False