#!/usr/bin/env python3
"""
Test script to verify post like toggle functionality
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com"
}

def test_post_like_toggle():
    print("🧪 Testing Post Like Toggle Functionality")
    print("=" * 50)
    
    # Step 1: Create a test user
    print("1. Creating test user...")
    try:
        response = requests.post(f"{BASE_URL}/users", json=TEST_USER)
        if response.status_code == 201:
            print("   ✅ User created successfully")
        elif response.status_code == 400 and "already exists" in response.text:
            print("   ⚠️  User already exists (continuing...)")
        else:
            print(f"   ❌ Failed to create user: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error creating user: {e}")
        return
    
    # Step 2: Login to get access token
    print("2. Logging in...")
    try:
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        response = requests.post(f"{BASE_URL}/users/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("   ✅ Login successful")
        else:
            print(f"   ❌ Login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error logging in: {e}")
        return
    
    # Step 3: Create a test post
    print("3. Creating test post...")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        post_data = {
            "title": "Test Post for Like Toggle",
            "content": "This is a test post to verify like toggle functionality"
        }
        response = requests.post(f"{BASE_URL}/posts", data=post_data, headers=headers)
        if response.status_code == 201:
            post = response.json()
            post_id = post["id"]
            initial_likes = post["likes"]
            print(f"   ✅ Post created with ID: {post_id}")
            print(f"   📊 Initial likes: {initial_likes}")
        else:
            print(f"   ❌ Failed to create post: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error creating post: {e}")
        return
    
    # Step 4: Test like toggle (first like)
    print("4. Testing first like...")
    try:
        response = requests.post(f"{BASE_URL}/posts/{post_id}/like", headers=headers)
        if response.status_code == 200:
            result = response.json()
            new_likes = result["likes"]
            liked_status = result["likedByCurrentUser"]
            print(f"   ✅ Like successful")
            print(f"   📊 Likes: {initial_likes} → {new_likes}")
            print(f"   ❤️  Liked by current user: {liked_status}")
            
            if new_likes == initial_likes + 1 and liked_status == True:
                print("   ✅ Like behavior correct")
            else:
                print("   ❌ Like behavior incorrect")
                return
        else:
            print(f"   ❌ Like failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error liking post: {e}")
        return
    
    # Step 5: Test like toggle (unlike)
    print("5. Testing unlike...")
    try:
        response = requests.post(f"{BASE_URL}/posts/{post_id}/like", headers=headers)
        if response.status_code == 200:
            result = response.json()
            final_likes = result["likes"]
            liked_status = result["likedByCurrentUser"]
            print(f"   ✅ Unlike successful")
            print(f"   📊 Likes: {new_likes} → {final_likes}")
            print(f"   ❤️  Liked by current user: {liked_status}")
            
            if final_likes == new_likes - 1 and liked_status == False:
                print("   ✅ Unlike behavior correct")
            else:
                print("   ❌ Unlike behavior incorrect")
                return
        else:
            print(f"   ❌ Unlike failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error unliking post: {e}")
        return
    
    # Step 5.5: Test multiple unlikes (should stay at 0)
    print("5.5. Testing multiple unlikes (should stay at 0)...")
    try:
        response = requests.post(f"{BASE_URL}/posts/{post_id}/like", headers=headers)
        if response.status_code == 200:
            result = response.json()
            multiple_unlike_likes = result["likes"]
            liked_status = result["likedByCurrentUser"]
            print(f"   📊 Likes after multiple unlike: {final_likes} → {multiple_unlike_likes}")
            print(f"   ❤️  Liked by current user: {liked_status}")
            
            if multiple_unlike_likes == 0 and liked_status == False:
                print("   ✅ Multiple unlike behavior correct (stays at 0)")
            else:
                print("   ❌ Multiple unlike behavior incorrect")
                return
        else:
            print(f"   ❌ Multiple unlike failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error multiple unliking post: {e}")
        return
    
    # Step 6: Test like toggle again (re-like)
    print("6. Testing re-like...")
    try:
        response = requests.post(f"{BASE_URL}/posts/{post_id}/like", headers=headers)
        if response.status_code == 200:
            result = response.json()
            re_likes = result["likes"]
            liked_status = result["likedByCurrentUser"]
            print(f"   ✅ Re-like successful")
            print(f"   📊 Likes: {final_likes} → {re_likes}")
            print(f"   ❤️  Liked by current user: {liked_status}")
            
            if re_likes == final_likes + 1 and liked_status == True:
                print("   ✅ Re-like behavior correct")
            else:
                print("   ❌ Re-like behavior incorrect")
                return
        else:
            print(f"   ❌ Re-like failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error re-liking post: {e}")
        return
    
    print("\n🎉 All tests passed! Post like toggle functionality is working correctly.")
    print("=" * 50)

if __name__ == "__main__":
    test_post_like_toggle() 