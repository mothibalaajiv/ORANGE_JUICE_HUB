import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const Home = () => {
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [productsRes, brandsRes] = await Promise.all([
          api.get('/products?limit=8'),
          api.get('/brands?limit=6')
        ]);
        
        setFeaturedProducts(productsRes.data.products);
        setBrands(brandsRes.data.brands);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-orange via-secondary-lightOrange via-citrus-500 to-secondary-darkOrange text-white py-24 px-4 overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 text-6xl filter drop-shadow-lg">🍊</div>
          <div className="absolute top-32 right-20 text-4xl filter drop-shadow-lg">🧃</div>
          <div className="absolute bottom-20 left-1/4 text-5xl filter drop-shadow-lg">🥤</div>
          <div className="absolute bottom-32 right-1/3 text-3xl filter drop-shadow-lg">🍋</div>
        </div>
        
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="animate-fade-in">
              <div className="inline-block bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium mb-6">
                🍊 Tangy Town - Fresh Juices Delivered
              </div>
              <h1 className="text-6xl md:text-7xl font-bold mb-6 leading-tight">
                Fresh Juices,<br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-citrus-200">
                  Delivered to Your Door!
                </span>
              </h1>
              <p className="text-xl mb-8 text-white/90 leading-relaxed">
                Discover premium orange and white juices from top brands like Tropicana,
                Real, and Minute Maid. Order now and enjoy lightning-fast delivery!
              </p>
              <div className="flex flex-wrap gap-4">
                <Link
                  to="/products"
                  className="bg-white text-primary-orange px-8 py-4 rounded-xl font-bold text-lg hover:bg-neutral-lightGray hover:scale-105 transition-all duration-300 shadow-xl"
                >
                  🛒 Shop Now
                </Link>
                <Link
                  to="/brands"
                  className="bg-transparent border-2 border-white/80 text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-white hover:text-primary-orange hover:scale-105 transition-all duration-300 backdrop-blur-sm"
                >
                  🏪 Explore Brands
                </Link>
              </div>
            </div>
            <div className="hidden lg:block">
              <div className="relative">
                <div className="text-9xl text-center filter drop-shadow-2xl animate-bounce-slow hover:scale-110 transition-all duration-500 hover:rotate-12 hover:brightness-110 hover:drop-shadow-[0_0_30px_rgba(255,165,0,0.6)]">🍊</div>
                <div className="absolute -bottom-6 -left-6 text-6xl animate-bounce hover:scale-110 transition-all duration-300 filter drop-shadow-lg hover:rotate-6 hover:brightness-110 hover:drop-shadow-[0_0_20px_rgba(255,255,255,0.4)]">🧃</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gradient-to-b from-neutral-lightGray to-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-neutral-black mb-4">
              Why Choose Tangy Town?
            </h2>
            <p className="text-neutral-darkGray text-lg max-w-2xl mx-auto">
              We're committed to delivering the freshest, most authentic juices with unmatched service quality.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="group bg-white p-8 rounded-2xl shadow-card hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border border-neutral-gray/20">
              <div className="bg-gradient-to-br from-primary-orange to-secondary-darkOrange w-16 h-16 rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:scale-110 transition-transform duration-300">
                <span className="text-2xl">🚚</span>
              </div>
              <h3 className="text-2xl font-bold mb-4 text-neutral-black text-center">Lightning Fast Delivery</h3>
              <p className="text-neutral-darkGray text-center leading-relaxed">
                Get your favorite juices delivered within minutes by our verified delivery partners. 
                Real-time tracking keeps you updated every step of the way.
              </p>
            </div>
            
            <div className="group bg-white p-8 rounded-2xl shadow-card hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border border-neutral-gray/20">
              <div className="bg-gradient-to-br from-citrus-400 to-citrus-600 w-16 h-16 rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:scale-110 transition-transform duration-300">
                <span className="text-2xl">✅</span>
              </div>
              <h3 className="text-2xl font-bold mb-4 text-neutral-black text-center">100% Authentic</h3>
              <p className="text-neutral-darkGray text-center leading-relaxed">
                All products sourced from verified supermarkets and authorized brands. 
                Every bottle is guaranteed fresh and authentic with full traceability.
              </p>
            </div>
            
            <div className="group bg-white p-8 rounded-2xl shadow-card hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border border-neutral-gray/20">
              <div className="bg-gradient-to-br from-secondary-yellow to-citrus-600 w-16 h-16 rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:scale-110 transition-transform duration-300">
                <span className="text-2xl">💳</span>
              </div>
              <h3 className="text-2xl font-bold mb-4 text-neutral-black text-center">Secure Payments</h3>
              <p className="text-neutral-darkGray text-center leading-relaxed">
                Safe and secure payments powered by Razorpay with multiple payment options. 
                Your financial data is protected with bank-level security.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <div className="inline-block bg-gradient-to-r from-primary-orange to-secondary-lightOrange px-6 py-2 rounded-full text-white text-sm font-medium mb-4">
              🍊 Fresh & Featured
            </div>
            <h2 className="text-5xl font-bold text-neutral-black mb-6">
              Featured Products
            </h2>
            <p className="text-neutral-darkGray text-xl max-w-2xl mx-auto leading-relaxed">
              Handpicked selections of the freshest and most loved juices from premium brands
            </p>
          </div>

          {loading ? (
            <div className="text-center py-16">
              <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-primary-orange border-t-transparent"></div>
              <p className="mt-4 text-neutral-darkGray">Loading fresh products...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              {featuredProducts.map((product) => (
                <Link
                  key={product._id}
                  to={`/products/${product._id}`}
                  className="group bg-white rounded-2xl shadow-card overflow-hidden hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border border-neutral-gray/20"
                >
                  <div className="relative h-56 bg-gradient-to-br from-neutral-lightGray to-neutral-gray overflow-hidden">
                    {product.imageUrl ? (
                      <img
                        src={product.imageUrl}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-8xl">🧃</div>
                    )}
                    <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-bold text-primary-orange">
                      Featured
                    </div>
                  </div>
                  <div className="p-6">
                    {product.brand && (
                      <p className="text-xs text-neutral-darkGray mb-2 font-medium uppercase tracking-wide">{product.brand.name}</p>
                    )}
                    <h3 className="font-bold text-neutral-black mb-3 text-lg line-clamp-2 group-hover:text-primary-orange transition-colors">
                      {product.name}
                    </h3>
                    <p className="text-sm text-neutral-darkGray mb-4">{product.volume}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-3xl font-bold bg-gradient-to-r from-primary-orange to-secondary-darkOrange bg-clip-text text-transparent">
                        ₹{product.price}
                      </span>
                      <button className="bg-gradient-to-r from-primary-orange to-secondary-darkOrange text-white px-6 py-3 rounded-xl text-sm font-bold hover:from-secondary-darkOrange hover:to-primary-orange hover:scale-105 transition-all duration-300 shadow-lg">
                        Add to Cart
                      </button>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}

          <div className="text-center mt-16">
            <Link
              to="/products"
              className="inline-block bg-gradient-to-r from-primary-orange to-secondary-darkOrange text-white px-10 py-4 rounded-xl font-bold text-lg hover:from-secondary-darkOrange hover:to-primary-orange hover:scale-105 transition-all duration-300 shadow-xl"
            >
              🛒 View All Products
            </Link>
          </div>
        </div>
      </section>

      {/* Featured Brands */}
      <section className="py-20 bg-gradient-to-b from-neutral-lightGray to-neutral-gray">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <div className="inline-block bg-gradient-to-r from-citrus-400 to-citrus-600 px-6 py-2 rounded-full text-white text-sm font-medium mb-4">
              🏆 Trusted Partners
            </div>
            <h2 className="text-5xl font-bold text-neutral-black mb-6">
              Popular Brands
            </h2>
            <p className="text-neutral-darkGray text-xl max-w-2xl mx-auto leading-relaxed">
              Shop from your favorite trusted juice brands, all verified and authentic
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {brands.map((brand) => (
              <Link
                key={brand._id}
                to={`/products?brandId=${brand._id}`}
                className="group bg-white p-8 rounded-2xl shadow-card flex items-center justify-center hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border border-neutral-gray/20"
              >
                {brand.logoUrl ? (
                  <img
                    src={brand.logoUrl}
                    alt={brand.name}
                    className="max-w-full max-h-16 object-contain group-hover:scale-110 transition-transform duration-300"
                  />
                ) : (
                  <span className="font-bold text-neutral-black group-hover:text-primary-orange transition-colors">{brand.name}</span>
                )}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-primary-orange via-secondary-darkOrange to-citrus-600 text-white relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 text-6xl animate-bounce filter drop-shadow-lg">🍊</div>
          <div className="absolute top-32 right-20 text-4xl animate-pulse filter drop-shadow-lg">🧃</div>
          <div className="absolute bottom-20 left-1/4 text-5xl animate-bounce filter drop-shadow-lg">🥤</div>
          <div className="absolute bottom-32 right-1/3 text-3xl animate-pulse filter drop-shadow-lg">🍋</div>
        </div>
        
        <div className="max-w-5xl mx-auto px-4 text-center relative z-10">
          <div className="inline-block bg-white/20 backdrop-blur-sm px-6 py-2 rounded-full text-sm font-medium mb-6">
            🚀 Join the Fresh Revolution
          </div>
          <h2 className="text-6xl md:text-7xl font-bold mb-8 leading-tight">
            Ready to Start Your
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-yellow-200">
              Fresh Journey?
            </span>
          </h2>
          <p className="text-2xl mb-12 text-white/90 max-w-3xl mx-auto leading-relaxed">
            Join thousands of satisfied customers enjoying fresh, authentic juices delivered lightning-fast to their doorstep!
          </p>
          <div className="flex flex-wrap justify-center gap-6">
            <Link
              to="/signup"
              className="bg-white text-primary-orange px-10 py-5 rounded-2xl font-bold text-xl hover:bg-neutral-lightGray hover:scale-105 transition-all duration-300 shadow-2xl"
            >
              🎉 Sign Up Now
            </Link>
            <Link
              to="/products"
              className="bg-transparent border-2 border-white/80 text-white px-10 py-5 rounded-2xl font-bold text-xl hover:bg-white hover:text-primary-orange hover:scale-105 transition-all duration-300 backdrop-blur-sm"
            >
              🛒 Start Shopping
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
