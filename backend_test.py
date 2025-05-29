
import requests
import sys
import json
from datetime import datetime

class ArtistPortfolioTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.artwork_id = None  # Will store an artwork ID for detailed tests

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                    return False, response.json()
                except:
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_get_all_artworks(self):
        """Test getting all artworks"""
        success, response = self.run_test(
            "Get All Artworks",
            "GET",
            "api/artworks",
            200
        )
        if success and isinstance(response, list) and len(response) > 0:
            print(f"Found {len(response)} artworks")
            # Store an artwork ID for later tests
            self.artwork_id = response[0]['id']
            return True
        return False

    def test_get_artwork_by_id(self):
        """Test getting a specific artwork by ID"""
        if not self.artwork_id:
            print("❌ No artwork ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Artwork by ID",
            "GET",
            f"api/artworks/{self.artwork_id}",
            200
        )
        if success and 'id' in response and response['id'] == self.artwork_id:
            print(f"Successfully retrieved artwork: {response['title']}")
            return True
        return False

    def test_get_artworks_by_category(self):
        """Test filtering artworks by category"""
        categories = ['abstract', 'landscape', 'digital']
        all_passed = True
        
        for category in categories:
            success, response = self.run_test(
                f"Get Artworks by Category: {category}",
                "GET",
                f"api/artworks?category={category}",
                200
            )
            if success and isinstance(response, list):
                print(f"Found {len(response)} artworks in category '{category}'")
                # Verify all returned artworks have the correct category
                if all(artwork['category'] == category for artwork in response):
                    print(f"✅ All returned artworks have category '{category}'")
                else:
                    print(f"❌ Some artworks have incorrect category")
                    all_passed = False
            else:
                all_passed = False
                
        return all_passed

    def test_get_featured_artworks(self):
        """Test getting featured artworks"""
        success, response = self.run_test(
            "Get Featured Artworks",
            "GET",
            "api/featured-artworks",
            200
        )
        if success and isinstance(response, list):
            print(f"Found {len(response)} featured artworks")
            return True
        return False

    def test_add_to_cart(self):
        """Test adding an artwork to cart"""
        if not self.artwork_id:
            print("❌ No artwork ID available for testing")
            return False
            
        cart_data = {
            "artwork_id": self.artwork_id,
            "quantity": 1
        }
        
        success, response = self.run_test(
            "Add to Cart",
            "POST",
            "api/cart/add",
            200,
            data=cart_data
        )
        return success

    def test_checkout_session(self):
        """Test creating a checkout session"""
        if not self.artwork_id:
            print("❌ No artwork ID available for testing")
            return False
            
        checkout_data = {
            "items": [
                {
                    "artwork_id": self.artwork_id,
                    "quantity": 1
                }
            ],
            "customer_email": "test@example.com"
        }
        
        success, response = self.run_test(
            "Create Checkout Session",
            "POST",
            "api/checkout/create-session",
            200,
            data=checkout_data
        )
        
        if success and 'session_id' in response and 'session_url' in response:
            print(f"Successfully created checkout session with ID: {response['session_id']}")
            return True
        return False

def main():
    # Get the backend URL from environment variable or use default
    backend_url = "https://b53e54d0-03b2-4a93-9b74-3e843efe8655.preview.emergentagent.com"
    
    print(f"🚀 Testing Artist Portfolio API at {backend_url}")
    
    # Initialize tester
    tester = ArtistPortfolioTester(backend_url)
    
    # Run tests
    tests = [
        ("Get All Artworks", tester.test_get_all_artworks),
        ("Get Artwork by ID", tester.test_get_artwork_by_id),
        ("Get Artworks by Category", tester.test_get_artworks_by_category),
        ("Get Featured Artworks", tester.test_get_featured_artworks),
        ("Add to Cart", tester.test_add_to_cart),
        ("Create Checkout Session", tester.test_checkout_session)
    ]
    
    for test_name, test_func in tests:
        print(f"\n📋 Running test: {test_name}")
        result = test_func()
        print(f"Result: {'✅ Passed' if result else '❌ Failed'}")
    
    # Print summary
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
