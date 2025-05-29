import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [artworks, setArtworks] = useState([]);
  const [featuredArtworks, setFeaturedArtworks] = useState([]);
  const [selectedArtwork, setSelectedArtwork] = useState(null);
  const [currentView, setCurrentView] = useState('home');
  const [filterCategory, setFilterCategory] = useState('all');
  const [cart, setCart] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isCheckingOut, setIsCheckingOut] = useState(false);

  useEffect(() => {
    fetchArtworks();
    fetchFeaturedArtworks();
    
    // Check if returning from Stripe success
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    if (sessionId) {
      setCurrentView('success');
    }
  }, [filterCategory]);

  const fetchArtworks = async () => {
    try {
      const url = filterCategory === 'all' 
        ? `${API_BASE_URL}/api/artworks`
        : `${API_BASE_URL}/api/artworks?category=${filterCategory}`;
      const response = await fetch(url);
      const data = await response.json();
      setArtworks(data);
    } catch (error) {
      console.error('Error fetching artworks:', error);
    }
  };

  const fetchFeaturedArtworks = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/featured-artworks`);
      const data = await response.json();
      setFeaturedArtworks(data);
    } catch (error) {
      console.error('Error fetching featured artworks:', error);
    }
  };

  const addToCart = (artwork) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.id === artwork.id);
      if (existingItem) {
        return prevCart.map(item =>
          item.id === artwork.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prevCart, { ...artwork, quantity: 1 }];
    });
  };

  const removeFromCart = (artworkId) => {
    setCart(prevCart => prevCart.filter(item => item.id !== artworkId));
  };

  const updateCartQuantity = (artworkId, quantity) => {
    if (quantity === 0) {
      removeFromCart(artworkId);
      return;
    }
    setCart(prevCart =>
      prevCart.map(item =>
        item.id === artworkId ? { ...item, quantity } : item
      )
    );
  };

  const getCartTotal = () => {
    return cart.reduce((total, item) => total + item.price * item.quantity, 0);
  };

  const handleCheckout = async () => {
    if (cart.length === 0) {
      alert('Your cart is empty!');
      return;
    }

    setIsCheckingOut(true);
    
    try {
      const checkoutData = {
        items: cart.map(item => ({
          artwork_id: item.id,
          quantity: item.quantity
        })),
        customer_email: 'customer@example.com' // In production, get from form
      };

      const response = await fetch(`${API_BASE_URL}/api/checkout/create-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(checkoutData),
      });

      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }

      const data = await response.json();
      
      // Redirect to Stripe checkout
      window.location.href = data.session_url;
      
    } catch (error) {
      console.error('Checkout error:', error);
      alert('Failed to start checkout. Please try again.');
    } finally {
      setIsCheckingOut(false);
    }
  };

  const Header = () => (
    <header className="header">
      <div className="container">
        <h1 className="logo" onClick={() => setCurrentView('home')}>
          Azure Gallery
        </h1>
        <nav className="nav">
          <button 
            className={currentView === 'home' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setCurrentView('home')}
          >
            Home
          </button>
          <button 
            className={currentView === 'gallery' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setCurrentView('gallery')}
          >
            Gallery
          </button>
          <button 
            className={currentView === 'about' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setCurrentView('about')}
          >
            About
          </button>
          <button 
            className={currentView === 'contact' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setCurrentView('contact')}
          >
            Contact
          </button>
          <button 
            className="cart-btn"
            onClick={() => setIsCartOpen(!isCartOpen)}
          >
            Cart ({cart.length})
          </button>
        </nav>
      </div>
    </header>
  );

  const HomePage = () => (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h2 className="hero-title">Contemporary Art That Speaks to the Soul</h2>
          <p className="hero-subtitle">
            Discover unique abstract and landscape paintings that transform spaces and inspire emotions
          </p>
          <button 
            className="cta-btn"
            onClick={() => setCurrentView('gallery')}
          >
            Explore Gallery
          </button>
        </div>
        <div className="hero-image">
          <img 
            src="https://images.unsplash.com/photo-1595878715977-2e8f8df18ea8" 
            alt="Featured Artwork"
            className="hero-artwork"
          />
        </div>
      </section>

      {/* About Preview */}
      <section className="about-preview">
        <div className="container">
          <h3>About the Artist</h3>
          <p>
            Welcome to my artistic journey. I create contemporary paintings that blend abstract expression 
            with natural landscapes, using rich textures and vibrant colors to evoke emotion and contemplation.
            Each piece is crafted with passion and designed to bring beauty into your living space.
          </p>
        </div>
      </section>

      {/* Featured Artworks */}
      <section className="featured-section">
        <div className="container">
          <h3>Featured Artworks</h3>
          <div className="featured-grid">
            {featuredArtworks.map(artwork => (
              <div key={artwork.id} className="featured-card">
                <img 
                  src={artwork.image_url} 
                  alt={artwork.title}
                  onClick={() => {
                    setSelectedArtwork(artwork);
                    setCurrentView('artwork-detail');
                  }}
                />
                <h4>{artwork.title}</h4>
                <p className="price">${artwork.price.toFixed(2)}</p>
                <button 
                  className="add-to-cart-btn"
                  onClick={() => addToCart(artwork)}
                >
                  Add to Cart
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter */}
      <section className="newsletter">
        <div className="container">
          <h3>Stay Updated</h3>
          <p>Get notifications about new artwork releases and exclusive previews</p>
          <div className="newsletter-form">
            <input type="email" placeholder="Enter your email" />
            <button>Subscribe</button>
          </div>
        </div>
      </section>
    </div>
  );

  const GalleryPage = () => (
    <div className="gallery-page">
      <div className="container">
        <h2>Art Gallery</h2>
        
        {/* Filters */}
        <div className="filters">
          <button 
            className={filterCategory === 'all' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilterCategory('all')}
          >
            All
          </button>
          <button 
            className={filterCategory === 'abstract' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilterCategory('abstract')}
          >
            Abstract
          </button>
          <button 
            className={filterCategory === 'landscape' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilterCategory('landscape')}
          >
            Landscape
          </button>
          <button 
            className={filterCategory === 'digital' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilterCategory('digital')}
          >
            Digital
          </button>
        </div>

        {/* Artwork Grid */}
        <div className="artwork-grid">
          {artworks.map(artwork => (
            <div key={artwork.id} className="artwork-card">
              <div className="artwork-image-container">
                <img 
                  src={artwork.image_url} 
                  alt={artwork.title}
                  className="artwork-image"
                  onClick={() => {
                    setSelectedArtwork(artwork);
                    setCurrentView('artwork-detail');
                  }}
                />
                <div className="artwork-overlay">
                  <button 
                    className="view-details-btn"
                    onClick={() => {
                      setSelectedArtwork(artwork);
                      setCurrentView('artwork-detail');
                    }}
                  >
                    View Details
                  </button>
                </div>
              </div>
              <div className="artwork-info">
                <h3>{artwork.title}</h3>
                <p className="medium">{artwork.medium}</p>
                <p className="size">{artwork.size}</p>
                <p className="price">${artwork.price.toFixed(2)}</p>
                <button 
                  className="add-to-cart-btn"
                  onClick={() => addToCart(artwork)}
                >
                  Add to Cart
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const ArtworkDetailPage = () => (
    <div className="artwork-detail-page">
      {selectedArtwork && (
        <div className="container">
          <button 
            className="back-btn"
            onClick={() => setCurrentView('gallery')}
          >
            ← Back to Gallery
          </button>
          
          <div className="artwork-detail">
            <div className="artwork-image-large">
              <img 
                src={selectedArtwork.image_url} 
                alt={selectedArtwork.title}
              />
            </div>
            
            <div className="artwork-details">
              <h2>{selectedArtwork.title}</h2>
              <p className="price-large">${selectedArtwork.price.toFixed(2)}</p>
              
              <div className="artwork-specs">
                <p><strong>Medium:</strong> {selectedArtwork.medium}</p>
                <p><strong>Size:</strong> {selectedArtwork.size}</p>
                <p><strong>Year:</strong> {selectedArtwork.year_created}</p>
                <p><strong>Category:</strong> {selectedArtwork.category}</p>
                <p><strong>Availability:</strong> {selectedArtwork.availability}</p>
              </div>
              
              <div className="description">
                <h4>Description</h4>
                <p>{selectedArtwork.description}</p>
              </div>
              
              <div className="action-buttons">
                <button 
                  className="add-to-cart-btn large"
                  onClick={() => addToCart(selectedArtwork)}
                >
                  Add to Cart
                </button>
                <button className="share-btn">Share</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const AboutPage = () => (
    <div className="about-page">
      <div className="container">
        <h2>About the Artist</h2>
        <div className="about-content">
          <div className="artist-photo">
            <img 
              src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d" 
              alt="Artist Portrait"
            />
          </div>
          <div className="artist-bio">
            <h3>Sarah Azure</h3>
            <p>
              Sarah Azure is a contemporary artist whose work explores the intersection of abstract expression 
              and natural landscapes. With over 15 years of experience, she has developed a unique style that 
              combines traditional painting techniques with modern artistic vision.
            </p>
            <p>
              Her paintings are characterized by flowing forms, rich textures, and a masterful use of color 
              that creates emotional depth and visual harmony. Each piece tells a story of connection between 
              the human spirit and the natural world.
            </p>
            <p>
              Sarah's work has been featured in galleries across the country and is held in private collections 
              worldwide. She continues to push the boundaries of contemporary art while maintaining a deep 
              respect for classical artistic traditions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const ContactPage = () => (
    <div className="contact-page">
      <div className="container">
        <h2>Contact</h2>
        <div className="contact-content">
          <div className="contact-form">
            <h3>Get in Touch</h3>
            <form>
              <input type="text" placeholder="Your Name" required />
              <input type="email" placeholder="Your Email" required />
              <textarea placeholder="Your Message" rows="5" required></textarea>
              <button type="submit">Send Message</button>
            </form>
          </div>
          <div className="contact-info">
            <h3>Contact Information</h3>
            <p><strong>Email:</strong> sarah@azuregallery.com</p>
            <p><strong>Phone:</strong> (555) 123-4567</p>
            <p><strong>Studio:</strong> 123 Art District, Creative City, CA 90210</p>
            
            <h4>Follow Me</h4>
            <div className="social-links">
              <a href="#" target="_blank" rel="noopener noreferrer">Instagram</a>
              <a href="#" target="_blank" rel="noopener noreferrer">Facebook</a>
              <a href="#" target="_blank" rel="noopener noreferrer">Twitter</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const SuccessPage = () => (
    <div className="success-page">
      <div className="container">
        <div className="success-content">
          <div className="success-icon">✅</div>
          <h2>Payment Successful!</h2>
          <p>Thank you for your purchase. Your order has been confirmed and will be processed shortly.</p>
          <p>You will receive an email confirmation with your order details and tracking information.</p>
          <button 
            className="cta-btn"
            onClick={() => {
              setCart([]);
              setCurrentView('home');
            }}
          >
            Continue Shopping
          </button>
        </div>
      </div>
    </div>
  );

  const Cart = () => (
    <div className={`cart-sidebar ${isCartOpen ? 'open' : ''}`}>
      <div className="cart-header">
        <h3>Shopping Cart</h3>
        <button 
          className="close-cart"
          onClick={() => setIsCartOpen(false)}
        >
          ×
        </button>
      </div>
      
      <div className="cart-items">
        {cart.length === 0 ? (
          <p className="empty-cart">Your cart is empty</p>
        ) : (
          cart.map(item => (
            <div key={item.id} className="cart-item">
              <img src={item.image_url} alt={item.title} />
              <div className="item-details">
                <h4>{item.title}</h4>
                <p>${item.price.toFixed(2)}</p>
                <div className="quantity-controls">
                  <button onClick={() => updateCartQuantity(item.id, item.quantity - 1)}>-</button>
                  <span>{item.quantity}</span>
                  <button onClick={() => updateCartQuantity(item.id, item.quantity + 1)}>+</button>
                </div>
              </div>
              <button 
                className="remove-item"
                onClick={() => removeFromCart(item.id)}
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
      
      {cart.length > 0 && (
        <div className="cart-footer">
          <div className="cart-total">
            <strong>Total: ${getCartTotal().toFixed(2)}</strong>
          </div>
          <button 
            className="checkout-btn"
            onClick={handleCheckout}
            disabled={isCheckingOut}
          >
            {isCheckingOut ? 'Processing...' : 'Proceed to Checkout'}
          </button>
        </div>
      )}
    </div>
  );

  const renderCurrentView = () => {
    switch (currentView) {
      case 'home':
        return <HomePage />;
      case 'gallery':
        return <GalleryPage />;
      case 'artwork-detail':
        return <ArtworkDetailPage />;
      case 'about':
        return <AboutPage />;
      case 'contact':
        return <ContactPage />;
      default:
        return <HomePage />;
    }
  };

  return (
    <div className="App">
      <Header />
      {renderCurrentView()}
      <Cart />
      
      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>&copy; 2024 Azure Gallery. All rights reserved.</p>
          <div className="footer-links">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Shipping & Returns</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;