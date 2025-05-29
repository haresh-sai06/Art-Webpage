
import requests
import sys
import json
from datetime import datetime

class ArtistPortfolioAPITester:
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
                if response.content:
                    try:
                        return success, response.json()
                    except json.JSONDecodeError:
                        return success, response.text
                return success, None
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                return False, None

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_get_all_artworks(self):
        """Test getting all artworks"""
        success, response = self.run_test(
            "Get All Artworks",
            "GET",
            "api/artworks",
            200
        )
        if success and response:
            print(f"Found {len(response)} artworks")
            if len(response) > 0:
                self.artwork_id = response[0]['id']  # Store first artwork ID for later tests
                print(f"Selected artwork ID for detailed tests: {self.artwork_id}")
        return success

    def test_get_artwork_by_id(self):
        """Test getting a specific artwork by ID"""
        if not self.artwork_id:
            print("❌ Cannot test artwork details - no artwork ID available")
            return False
            
        success, response = self.run_test(
            "Get Artwork by ID",
            "GET",
            f"api/artworks/{self.artwork_id}",
            200
        )
        if success and response:
            print(f"Artwork details: {response['title']} - ${response['price']}")
        return success

    def test_get_artworks_by_category(self):
        """Test filtering artworks by category"""
        categories = ['abstract', 'landscape', 'digital']
        all_success = True
        
        for category in categories:
            success, response = self.run_test(
                f"Get Artworks by Category: {category}",
                "GET",
                f"api/artworks?category={category}",
                200
            )
            if success and response:
                print(f"Found {len(response)} artworks in category '{category}'")
                all_success = all_success and success
            else:
                all_success = False
                
        return all_success

    def test_get_featured_artworks(self):
        """Test getting featured artworks"""
        success, response = self.run_test(
            "Get Featured Artworks",
            "GET",
            "api/featured-artworks",
            200
        )
        if success and response:
            print(f"Found {len(response)} featured artworks")
        return success

    def test_add_to_cart(self):
        """Test adding an item to cart"""
        if not self.artwork_id:
            print("❌ Cannot test add to cart - no artwork ID available")
            return False
            
        cart_item = {
            "artwork_id": self.artwork_id,
            "quantity": 1
        }
        
        success, response = self.run_test(
            "Add to Cart",
            "POST",
            "api/cart/add",
            200,
            data=cart_item
        )
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("=" * 50)
        print("🧪 ARTIST PORTFOLIO API TESTS")
        print("=" * 50)
        
        # Run all tests
        self.test_get_all_artworks()
        self.test_get_artwork_by_id()
        self.test_get_artworks_by_category()
        self.test_get_featured_artworks()
        self.test_add_to_cart()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 SUMMARY: {self.tests_passed}/{self.tests_run} tests passed")
        print("=" * 50)
        
        return self.tests_passed == self.tests_run

def main():
    # Get backend URL from environment variable or use default
    backend_url = "https://b53e54d0-03b2-4a93-9b74-3e843efe8655.preview.emergentagent.com"
    
    print(f"Testing API at: {backend_url}")
    tester = ArtistPortfolioAPITester(backend_url)
    
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
