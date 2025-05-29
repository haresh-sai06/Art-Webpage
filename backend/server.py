from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import uuid
from pymongo import MongoClient
import uvicorn
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'artist_portfolio')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Stripe initialization
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
if not STRIPE_API_KEY:
    raise ValueError("STRIPE_API_KEY environment variable is required")

stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY)

# Collections
artworks_collection = db.artworks
orders_collection = db.orders
payment_transactions_collection = db.payment_transactions

# Pydantic models
class Artwork(BaseModel):
    id: str
    title: str
    price: float
    medium: str
    size: str
    year_created: int
    description: str
    image_url: str
    category: str
    availability: str  # "available", "sold"

class CartItem(BaseModel):
    artwork_id: str
    quantity: int = 1

class CheckoutRequest(BaseModel):
    items: List[CartItem]
    customer_email: Optional[str] = None

class Order(BaseModel):
    id: str
    items: List[CartItem]
    total_amount: float
    customer_email: str
    status: str  # "pending", "paid", "shipped", "completed"
    payment_session_id: Optional[str] = None

# Sample artwork data
sample_artworks = [
    {
        "id": str(uuid.uuid4()),
        "title": "Azure Dreams",
        "price": 850.00,
        "medium": "Acrylic on Canvas",
        "size": "24\" x 36\"",
        "year_created": 2024,
        "description": "A mesmerizing abstract composition featuring flowing blue and white elements that evoke the tranquility of ocean waves and sky.",
        "image_url": "https://images.unsplash.com/photo-1595878715977-2e8f8df18ea8",
        "category": "abstract",
        "availability": "available"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Dynamic Blue",
        "price": 720.00,
        "medium": "Oil on Canvas",
        "size": "20\" x 24\"",
        "year_created": 2024,
        "description": "Bold abstract expressionism with powerful blue and white strokes creating movement and energy.",
        "image_url": "https://images.unsplash.com/photo-1550843739-2e9e3eddeccb",
        "category": "abstract",
        "availability": "available"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Textured Serenity",
        "price": 950.00,
        "medium": "Mixed Media",
        "size": "30\" x 40\"",
        "year_created": 2023,
        "description": "Rich textural elements combined with soothing blue tones create depth and contemplative beauty.",
        "image_url": "https://images.unsplash.com/photo-1558447281-b59a4a4ca7b0",
        "category": "abstract",
        "availability": "available"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Peaceful Valley",
        "price": 1200.00,
        "medium": "Oil on Canvas",
        "size": "36\" x 48\"",
        "year_created": 2024,
        "description": "A serene landscape capturing the quiet beauty of rolling hills under an expansive blue sky.",
        "image_url": "https://images.unsplash.com/photo-1661089359976-de812515d817",
        "category": "landscape",
        "availability": "available"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Mountain Majesty",
        "price": 1450.00,
        "medium": "Acrylic on Canvas",
        "size": "40\" x 60\"",
        "year_created": 2023,
        "description": "Majestic mountain peaks painted with atmospheric perspective and beautiful blue atmospheric effects.",
        "image_url": "https://images.unsplash.com/photo-1648728066884-74aaf02585a5",
        "category": "landscape",
        "availability": "available"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Sky Dreams",
        "price": 675.00,
        "medium": "Digital Art Print",
        "size": "18\" x 24\"",
        "year_created": 2024,
        "description": "An artistic interpretation of sky and clouds with creative blue elements and modern composition.",
        "image_url": "https://images.unsplash.com/photo-1594201272716-9ad78d16848b",
        "category": "digital",
        "availability": "available"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Fluid Harmony",
        "price": 780.00,
        "medium": "Pour Painting",
        "size": "24\" x 30\"",
        "year_created": 2024,
        "description": "A beautiful fluid art piece with marbled blue, green, and pink tones creating organic harmony.",
        "image_url": "https://images.unsplash.com/photo-1614519679717-a75c4201c2df",
        "category": "abstract",
        "availability": "available"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Digital Visions",
        "price": 525.00,
        "medium": "Digital Art Print",
        "size": "16\" x 20\"",
        "year_created": 2024,
        "description": "Contemporary digital artwork featuring blue tones and artistic composition with modern appeal.",
        "image_url": "https://images.unsplash.com/photo-1551596210-4da509bd1e99",
        "category": "digital",
        "availability": "available"
    }
]

@app.on_event("startup")
async def startup_event():
    # Initialize sample data if collection is empty
    if artworks_collection.count_documents({}) == 0:
        artworks_collection.insert_many(sample_artworks)

@app.get("/")
async def root():
    return {"message": "Artist Portfolio API"}

# Artwork endpoints
@app.get("/api/artworks")
async def get_artworks(category: Optional[str] = None, availability: Optional[str] = None):
    query = {}
    if category:
        query["category"] = category
    if availability:
        query["availability"] = availability
    
    artworks = list(artworks_collection.find(query, {"_id": 0}))
    return artworks

@app.get("/api/artworks/{artwork_id}")
async def get_artwork(artwork_id: str):
    artwork = artworks_collection.find_one({"id": artwork_id}, {"_id": 0})
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return artwork

# Featured artworks for homepage
@app.get("/api/featured-artworks")
async def get_featured_artworks():
    # Return first 3 available artworks as featured
    artworks = list(artworks_collection.find({"availability": "available"}, {"_id": 0}).limit(3))
    return artworks

# Cart and order endpoints (basic structure for now)
@app.post("/api/cart/add")
async def add_to_cart(item: CartItem):
    # For now, just validate artwork exists
    artwork = artworks_collection.find_one({"id": item.artwork_id}, {"_id": 0})
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return {"message": "Item added to cart", "item": item}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)