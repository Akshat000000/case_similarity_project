import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def check_backend_health():
    """Checks if the backend API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False

def search_cases(query_text: str):
    """
    Calls the backend /search endpoint.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/search", 
            json={"query": query_text},
            timeout=120  # Search might take time (increased for slow hardware/cold start)
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Search API Error: {response.text}")
            return []
    except Exception as e:
        st.error(f"Failed to connect to Search API: {str(e)}")
        return []

def fetch_random_cases(limit: int = 10):
    """
    Calls the backend /cases/random endpoint.
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/cases/random", 
            params={"limit": limit},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error fetching cases: {response.text}")
            return []
    except Exception as e:
        st.error("Could not connect to backend API. Is it running?")
        return []

def fetch_case_details(case_id: str):
    """
    Calls the backend /cases/{case_id} endpoint.
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/cases/{case_id}",
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.error("Case not found.")
            return None
        else:
            st.error(f"API Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Failed to fetch case details: {str(e)}")
        return None
