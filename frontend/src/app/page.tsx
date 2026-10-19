'use client';

import React, { useState, useEffect } from 'react';
import { api, Product, Cart, Order, User } from '@/lib/api';

export default function Storefront() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<Cart | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [inStockOnly, setInStockOnly] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [debouncedSearch, setDebouncedSearch] = useState<string>('');
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [initialLoading, setInitialLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'catalog' | 'orders'>('catalog');
  const [isCartOpen, setIsCartOpen] = useState<boolean>(false);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState<boolean>(false);
  const [isAuthOpen, setIsAuthOpen] = useState<boolean>(false);
  const [selectedProductDetail, setSelectedProductDetail] = useState<Product | null>(null);
  const [detailQty, setDetailQty] = useState<number>(1);

  // Notifications
  const [toastMsg, setToastMsg] = useState<{ text: string; isError?: boolean } | null>(null);

  // Checkout inputs
  const [paymentToken, setPaymentToken] = useState<string>('tok_success');
  const [shippingAddress, setShippingAddress] = useState<string>('');
  const [isProcessingCheckout, setIsProcessingCheckout] = useState<boolean>(false);
  const [checkoutError, setCheckoutError] = useState<string>('');

  // Auth inputs
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [authUsername, setAuthUsername] = useState<string>('');
  const [authPassword, setAuthPassword] = useState<string>('');
  const [authRole, setAuthRole] = useState<'customer' | 'admin'>('customer');

  // Admin stock update
  const [editingStockId, setEditingStockId] = useState<number | null>(null);
  const [newStockVal, setNewStockVal] = useState<number>(0);

  useEffect(() => {
    const user = api.getCurrentUser();
    setCurrentUser(user);
    if (user?.address) setShippingAddress(user.address);
    loadCart();
    if (user) loadOrders();
  }, [activeTab]);

  // Debounce search query by 280ms to avoid UI flickering and API spam
  useEffect(() => {
    if (searchQuery !== debouncedSearch) {
      setIsSearching(true);
    }
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 280);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch products whenever category, inStock filter, or debounced search changes
  useEffect(() => {
    loadProducts();
  }, [selectedCategory, inStockOnly, debouncedSearch]);

  const showToast = (text: string, isError = false) => {
    setToastMsg({ text, isError });
    setTimeout(() => setToastMsg(null), 4000);
  };

  const loadProducts = async () => {
    try {
      const data = await api.getProducts({
        category: selectedCategory || undefined,
        search: debouncedSearch || undefined,
        in_stock: inStockOnly || undefined,
      });
      setProducts(data);
    } catch (err: any) {
      showToast(err.message, true);
    } finally {
      setInitialLoading(false);
      setIsSearching(false);
    }
  };

  const loadCart = async () => {
    try {
      const user = api.getCurrentUser();
      if (!user) {
        const guestCartStr = localStorage.getItem('guest_cart');
        if (guestCartStr) {
          const guestItems = JSON.parse(guestCartStr);
          const totalItems = guestItems.reduce((acc: number, it: any) => acc + it.quantity, 0);
          const totalAmount = guestItems.reduce((acc: number, it: any) => acc + parseFloat(it.subtotal), 0).toFixed(2);
          setCart({
            id: 0,
            user: null,
            items: guestItems,
            total_items: totalItems,
            total_amount: totalAmount,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
        } else {
          setCart(null);
        }
        return;
      }
      const data = await api.getCart();
      setCart(data);
    } catch (err: any) {
      console.error(err);
    }
  };

  const loadOrders = async () => {
    try {
      const data = await api.getOrders();
      setOrders(data);
    } catch (err: any) {
      console.error(err);
    }
  };

  // Demo user fast switcher
  const switchDemoUser = async (username: string, pass: string) => {
    try {
      await api.login({ username, password: pass });
      const user = api.getCurrentUser();
      setCurrentUser(user);
      if (user?.address) setShippingAddress(user.address);
      showToast(`Switched account to @${username} (${user?.role.toUpperCase()})`);
      loadCart();
      loadOrders();
      loadProducts();
    } catch (err: any) {
      showToast(`Login failed: ${err.message}`, true);
    }
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
    setOrders([]);
    setActiveTab('catalog');
    showToast('Logged out to Guest Mode');
    loadCart();
    loadProducts();
  };

  const openProductDetail = (product: Product) => {
    setSelectedProductDetail(product);
    setDetailQty(1);
  };

  const handleAddToCart = async (product: Product, quantity = 1) => {
    try {
      if (!currentUser) {
        // Guest mode client cart in localStorage
        const guestCartStr = localStorage.getItem('guest_cart');
        let guestItems: any[] = guestCartStr ? JSON.parse(guestCartStr) : [];
        const existing = guestItems.find((it: any) => it.product.id === product.id);

        if (existing) {
          if (existing.quantity + quantity > product.stock) {
            throw new Error(`Cannot add more than available stock (${product.stock} available, you already have ${existing.quantity} in cart)`);
          }
          existing.quantity += quantity;
          existing.subtotal = (parseFloat(existing.product.price) * existing.quantity).toFixed(2);
        } else {
          if (quantity > product.stock) {
            throw new Error(`Cannot add more than available stock (${product.stock} available)`);
          }
          guestItems.push({
            id: Date.now(),
            product: product,
            quantity: quantity,
            subtotal: (parseFloat(product.price) * quantity).toFixed(2),
          });
        }

        localStorage.setItem('guest_cart', JSON.stringify(guestItems));
        const totalItems = guestItems.reduce((acc: number, it: any) => acc + it.quantity, 0);
        const totalAmount = guestItems.reduce((acc: number, it: any) => acc + parseFloat(it.subtotal), 0).toFixed(2);
        setCart({
          id: 0,
          user: null,
          items: guestItems,
          total_items: totalItems,
          total_amount: totalAmount,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
        showToast(`Added ${quantity}x '${product.title}' to Guest Cart!`);
        setIsCartOpen(true);
        return;
      }

      await api.addToCart(product.id, quantity);
      showToast(`Added ${quantity}x '${product.title}' to cart!`);
      loadCart();
      setIsCartOpen(true);
    } catch (err: any) {
      showToast(err.message, true);
    }
  };

  const handleBuyNowFromModal = async (product: Product, quantity: number) => {
    await handleAddToCart(product, quantity);
    setSelectedProductDetail(null);
    if (currentUser) {
      setIsCheckoutOpen(true);
    } else {
      showToast('Please sign in or select a customer profile to proceed with checkout.');
      setIsAuthOpen(true);
    }
  };

  const handleUpdateCartQty = async (itemId: number, newQty: number) => {
    try {
      if (!currentUser) {
        const guestCartStr = localStorage.getItem('guest_cart');
        let guestItems: any[] = guestCartStr ? JSON.parse(guestCartStr) : [];
        if (newQty <= 0) {
          guestItems = guestItems.filter((it: any) => it.id !== itemId);
        } else {
          const item = guestItems.find((it: any) => it.id === itemId);
          if (item) {
            item.quantity = newQty;
            item.subtotal = (parseFloat(item.product.price) * newQty).toFixed(2);
          }
        }
        localStorage.setItem('guest_cart', JSON.stringify(guestItems));
        loadCart();
        return;
      }

      await api.updateCartItem(itemId, newQty);
      loadCart();
    } catch (err: any) {
      showToast(err.message, true);
    }
  };

  const handleClearCart = async () => {
    try {
      if (!currentUser) {
        localStorage.removeItem('guest_cart');
        setCart(null);
        showToast('Guest cart cleared');
        return;
      }

      await api.clearCart();
      loadCart();
      showToast('Cart cleared');
    } catch (err: any) {
      showToast(err.message, true);
    }
  };

  const handleExecuteCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) {
      showToast('Please sign in or select a customer account to checkout.', true);
      setIsAuthOpen(true);
      return;
    }
    if (!cart || cart.items.length === 0) {
      showToast('Your cart is empty.', true);
      return;
    }

    setIsProcessingCheckout(true);
    setCheckoutError('');
    const idempotencyKey = 'IDEM-' + Math.random().toString(36).substring(2, 10).toUpperCase();

    try {
      const order = await api.checkout({
        payment_token: paymentToken,
        idempotency_key: idempotencyKey,
        shipping_address: shippingAddress,
      });

      showToast(`🎉 Order ${order.order_number} confirmed! Stock decremented and payment settled.`);
      setIsCheckoutOpen(false);
      setIsCartOpen(false);
      setCheckoutError('');
      loadCart();
      loadOrders();
      loadProducts();
      setActiveTab('orders');
    } catch (err: any) {
      setCheckoutError(err.message);
      showToast(`Checkout Error: ${err.message}`, true);
    } finally {
      setIsProcessingCheckout(false);
    }
  };

  const handleUpdateOrderStatus = async (orderId: number, newStatus: string) => {
    try {
      const updated = await api.updateOrderStatus(orderId, newStatus);
      showToast(`Order ${updated.order_number} transitioned to '${newStatus.toUpperCase()}'!`);
      loadOrders();
    } catch (err: any) {
      showToast(err.message, true);
    }
  };

  const handleSaveStockUpdate = async (productId: number) => {
    try {
      await api.updateStock(productId, newStockVal);
      showToast(`Stock updated to ${newStockVal} units!`);
      setEditingStockId(null);
      loadProducts();
      if (selectedProductDetail && selectedProductDetail.id === productId) {
        setSelectedProductDetail({
          ...selectedProductDetail,
          stock: newStockVal
        });
      }
    } catch (err: any) {
      showToast(err.message, true);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Toast Alert - z-[100] so it is always above all modal backdrops */}
      {toastMsg && (
        <div className={`fixed top-5 right-5 z-[100] text-white px-5 py-3 rounded-xl shadow-2xl flex items-center space-x-2 text-xs sm:text-sm font-semibold animate-fade-in ${toastMsg.isError ? 'bg-red-600 border border-red-400' : 'bg-emerald-600 border border-emerald-400'}`}>
          <span>{toastMsg.isError ? '⚠️' : '✅'}</span>
          <span>{toastMsg.text}</span>
        </div>
      )}

      {/* Header */}
      <header className="glass-nav text-white sticky top-0 z-40 border-b border-slate-800/80 bg-slate-900/95 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-600 flex items-center justify-center font-bold text-base shadow-lg">
              NM
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold tracking-tight text-lg text-white">NovaMart</span>
                <span className="text-xs uppercase px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold">
                  Store
                </span>
                <a
                  href="https://drive.google.com/file/d/188jZ0az2y0jtlESSNeMaqs3rUR2J5Tqg/view?usp=sharing"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hidden md:inline-flex items-center space-x-1 text-xs bg-red-600/90 hover:bg-red-500 text-white px-2.5 py-0.5 rounded-full font-bold shadow transition transform hover:scale-105"
                  title="Watch 3-5 Minute Demo Video Walkthrough"
                >
                  <span>▶️</span>
                  <span>Demo Video</span>
                </a>
              </div>
            </div>
          </div>

          {/* Quick Demo Switcher - Always Visible on All Screen Sizes */}
          <div className="flex flex-wrap items-center gap-1.5 bg-slate-950/80 p-1.5 rounded-xl border border-slate-700/60 text-xs">
            <span className="text-slate-400 px-1 font-medium text-[11px] hidden sm:inline">Demo Switch:</span>
            <button
              onClick={() => switchDemoUser('admin', 'Admin@123')}
              className={`px-2.5 py-1 rounded-lg transition text-xs ${currentUser?.username === 'admin' ? 'bg-indigo-600 text-white font-bold' : 'hover:bg-slate-800 text-slate-300'}`}
            >
              👑 Admin
            </button>
            <button
              onClick={() => switchDemoUser('talha_customer', 'Customer@123')}
              className={`px-2.5 py-1 rounded-lg transition text-xs ${currentUser?.username === 'talha_customer' ? 'bg-emerald-600 text-white font-bold' : 'hover:bg-slate-800 text-slate-300'}`}
            >
              🛒 Customer 1 (Talha)
            </button>
            <button
              onClick={() => switchDemoUser('alice_buyer', 'Password@123')}
              className={`px-2.5 py-1 rounded-lg transition text-xs ${currentUser?.username === 'alice_buyer' ? 'bg-emerald-600 text-white font-bold' : 'hover:bg-slate-800 text-slate-300'}`}
            >
              🛒 Alice Buyer
            </button>
            <button
              onClick={() => switchDemoUser('sara_shopper', 'Customer@123')}
              className={`px-2.5 py-1 rounded-lg transition text-xs ${currentUser?.username === 'sara_shopper' ? 'bg-emerald-600 text-white font-bold' : 'hover:bg-slate-800 text-slate-300'}`}
            >
              🛒 Sara (Peer)
            </button>
            <button
              onClick={handleLogout}
              className={`px-2 py-1 rounded-lg transition text-xs ${!currentUser ? 'bg-sky-600 text-white font-bold' : 'hover:bg-slate-800 text-slate-300'}`}
            >
              👀 Guest
            </button>
          </div>

          {/* Navigation & Cart Controls */}
          <div className="flex items-center space-x-2">
            {/* Primary View Switcher: Catalog vs Orders */}
            <div className="flex items-center space-x-1 bg-slate-950/80 p-1 rounded-xl border border-slate-700/60">
              <button
                onClick={() => setActiveTab('catalog')}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${
                  activeTab === 'catalog'
                    ? 'bg-emerald-600 text-white shadow-md'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <span>🛍️</span>
                <span>Store Catalog</span>
              </button>

              {currentUser && (
                <button
                  onClick={() => setActiveTab('orders')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${
                    activeTab === 'orders'
                      ? 'bg-emerald-600 text-white shadow-md'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <span>📦</span>
                  <span>{currentUser.role === 'admin' ? 'All Orders' : 'My Orders'} ({orders.length})</span>
                </button>
              )}
            </div>

            {/* Cart Trigger */}
            <button
              onClick={() => setIsCartOpen(true)}
              className="relative bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-1.5 rounded-lg text-xs font-bold shadow-md flex items-center space-x-2 transition"
            >
              <span>🛒</span>
              <span>Cart</span>
              <span className="bg-emerald-950 text-emerald-200 px-1.5 py-0.2 rounded-full text-[10px] font-black">
                {cart?.total_items || 0}
              </span>
            </button>

            {/* User status */}
            {currentUser ? (
              <div className="flex items-center space-x-2 pl-2 border-l border-slate-700">
                <div className="text-right text-xs">
                  <div className="font-bold text-slate-200">@{currentUser.username}</div>
                  <span className="text-[10px] uppercase font-semibold text-emerald-400 bg-emerald-950/60 px-1.5 py-0.2 rounded border border-emerald-800/60">
                    {currentUser.role}
                  </span>
                </div>
                <button onClick={handleLogout} className="text-slate-400 hover:text-red-400 text-xs p-1" title="Log Out">
                  ✕
                </button>
              </div>
            ) : (
              <button
                onClick={() => setIsAuthOpen(true)}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg text-xs font-bold transition border border-slate-700"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Dynamic Persona Status & Distinct Role Card */}
        <div className="mb-6 p-4 rounded-2xl border transition-all duration-300 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs bg-white">
          <div className="flex items-start md:items-center space-x-3">
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-base shrink-0 shadow-sm ${
              currentUser?.role === 'admin' 
                ? 'bg-indigo-600 text-white' 
                : currentUser?.username === 'talha_customer'
                ? 'bg-emerald-600 text-white'
                : currentUser?.username === 'alice_buyer'
                ? 'bg-sky-600 text-white'
                : currentUser
                ? 'bg-purple-600 text-white'
                : 'bg-slate-800 text-slate-200'
            }`}>
              {currentUser?.role === 'admin' ? '👑' : currentUser ? '🛒' : '👀'}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-sm text-slate-900">
                  {currentUser?.role === 'admin' 
                    ? 'Store Admin & Fulfillment Hub' 
                    : currentUser?.username === 'talha_customer'
                    ? 'Customer 1: Talha Ahmed (VIP Buyer)'
                    : currentUser?.username === 'alice_buyer'
                    ? 'Customer 2: Alice Buyer'
                    : currentUser?.username === 'sara_shopper'
                    ? 'Customer 3: Sara Shopper (Peer Customer)'
                    : 'Guest Browsing Mode'}
                </span>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider ${
                  currentUser?.role === 'admin' 
                    ? 'bg-indigo-100 text-indigo-800' 
                    : currentUser
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-slate-100 text-slate-700'
                }`}>
                  {currentUser ? `@${currentUser.username} (${currentUser.role})` : 'Unauthenticated'}
                </span>
              </div>
              <p className="text-slate-500 text-[11px] mt-0.5 leading-relaxed">
                {currentUser?.role === 'admin'
                  ? '👑 Full Store Authority: You see all customer orders across the platform (Talha, Alice, Sara) in "All Orders", and you have inventory update controls.'
                  : currentUser?.username === 'talha_customer'
                  ? '🛒 Showing Talha\'s private cart & orders (ORD-TALHA-001). Strict RBAC ensures Talha cannot view Alice\'s or Sara\'s orders.'
                  : currentUser?.username === 'alice_buyer'
                  ? '🛒 Showing Alice\'s private cart & orders (ORD-ALICE-102). Alice only sees her own purchase history.'
                  : currentUser?.username === 'sara_shopper'
                  ? '🛒 Showing Sara\'s private order history (ORD-D5D52C2C). Isolated peer customer account.'
                  : '👀 Guest Mode: You can browse all products and add items to your session cart. Switch to Talha or Alice to checkout.'}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            <a
              href="https://drive.google.com/file/d/188jZ0az2y0jtlESSNeMaqs3rUR2J5Tqg/view?usp=sharing"
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 rounded-lg text-xs font-bold bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white transition flex items-center gap-1.5 shadow-md transform hover:scale-105"
              title="Watch 3-5 Minute Demo Video Walkthrough"
            >
              <span>▶️</span>
              <span>Watch Demo Video</span>
            </a>
            {currentUser ? (
              <>
                {activeTab === 'orders' ? (
                  <button
                    onClick={() => setActiveTab('catalog')}
                    className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1.5 shadow-md"
                  >
                    <span>🛍️</span>
                    <span>Back to Store Catalog (6 Items)</span>
                  </button>
                ) : (
                  <button
                    onClick={() => setActiveTab('orders')}
                    className="px-3 py-1.5 rounded-lg text-xs font-bold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 transition flex items-center gap-1.5 shadow-sm"
                  >
                    <span>📦</span>
                    <span>{currentUser.role === 'admin' ? `View All Orders (${orders.length})` : `View My Orders (${orders.length})`}</span>
                  </button>
                )}
                <button
                  onClick={() => setIsCartOpen(true)}
                  className="px-3 py-1.5 rounded-lg text-xs font-bold bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 transition flex items-center gap-1.5 shadow-sm"
                >
                  <span>🛒</span>
                  <span>View Cart ({cart?.total_items || 0})</span>
                </button>
              </>
            ) : (
              <button
                onClick={() => setIsCartOpen(true)}
                className="px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 transition flex items-center gap-1.5 shadow-sm"
              >
                <span>🛒</span>
                <span>View Session Cart ({cart?.total_items || 0})</span>
              </button>
            )}
          </div>
        </div>

        {/* Hero Banner */}
        <div className="mb-8 p-8 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-emerald-950 text-white shadow-xl relative overflow-hidden border border-slate-800">
          <div className="relative z-10 max-w-2xl">
            <div className="inline-block px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 text-xs font-semibold uppercase tracking-wider mb-3">
              ACID Concurrency Guarantee • Zero Negative Stock
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-2">
              High-Integrity E-Commerce Storefront
            </h1>
            <p className="text-slate-300 text-sm leading-relaxed">
              Featuring row-level pessimistic locking (`select_for_update`), atomic inventory reservation, honest mock payment card simulation, and immutable historical price order receipts.
            </p>
          </div>
          <div className="absolute right-0 bottom-0 opacity-10 translate-x-10 translate-y-10 text-9xl font-black select-none pointer-events-none">
            ACID
          </div>
        </div>

        {/* Catalog View */}
        {activeTab === 'catalog' ? (
          <div>
            {/* Filter & Search Bar */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
              {/* Category Pills */}
              <div className="flex items-center space-x-2 overflow-x-auto pb-2 md:pb-0">
                <button
                  onClick={() => setSelectedCategory('')}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition ${selectedCategory === '' ? 'bg-emerald-600 text-white shadow' : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'}`}
                >
                  All Gear
                </button>
                <button
                  onClick={() => setSelectedCategory('electronics')}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition ${selectedCategory === 'electronics' ? 'bg-emerald-600 text-white shadow' : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'}`}
                >
                  Displays & Electronics
                </button>
                <button
                  onClick={() => setSelectedCategory('accessories')}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition ${selectedCategory === 'accessories' ? 'bg-emerald-600 text-white shadow' : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'}`}
                >
                  Developer Keyboards & Keycaps
                </button>
                <button
                  onClick={() => setSelectedCategory('audio')}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition ${selectedCategory === 'audio' ? 'bg-emerald-600 text-white shadow' : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'}`}
                >
                  Studio Audio
                </button>
                <button
                  onClick={() => setSelectedCategory('ergonomics')}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition ${selectedCategory === 'ergonomics' ? 'bg-emerald-600 text-white shadow' : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'}`}
                >
                  Standing Desks
                </button>
              </div>

              {/* In-Stock & Search Filters */}
              <div className="flex items-center space-x-3">
                <label className="flex items-center space-x-1.5 text-xs text-slate-700 bg-white px-3 py-1.5 rounded-lg border border-slate-200 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={inStockOnly}
                    onChange={(e) => setInStockOnly(e.target.checked)}
                    className="rounded text-emerald-600 focus:ring-emerald-500"
                  />
                  <span>In Stock Only</span>
                </label>

                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search catalog or SKU..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-8 pr-8 py-1.5 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white w-48 sm:w-64"
                  />
                  <span className="absolute left-2.5 top-2 text-slate-400 text-xs">🔍</span>
                  {isSearching ? (
                    <span className="absolute right-2.5 top-2 inline-block animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-emerald-600"></span>
                  ) : searchQuery ? (
                    <button
                      type="button"
                      onClick={() => setSearchQuery('')}
                      className="absolute right-2.5 top-1.5 text-slate-400 hover:text-slate-600 text-xs"
                    >
                      ✕
                    </button>
                  ) : null}
                </div>
              </div>
            </div>

            {/* Products Grid */}
            {initialLoading ? (
              <div className="text-center py-20 text-slate-400 text-sm">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500 mb-3"></div>
                <div>Querying real-time inventory from PostgreSQL...</div>
              </div>
            ) : products.length === 0 ? (
              <div className="text-center py-20 bg-white rounded-2xl border border-slate-200 p-8">
                <span className="text-4xl mb-3 block">📦</span>
                <h3 className="text-base font-bold text-slate-800">No products found</h3>
                <p className="text-slate-500 text-xs mt-1">Try clearing your filters or search terms.</p>
              </div>
            ) : (
              <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 transition-opacity duration-200 ${isSearching ? 'opacity-60' : 'opacity-100'}`}>
                {products.map((product) => {
                  const isOutOfStock = product.stock <= 0;
                  const isLowStock = product.stock === 1;

                  return (
                    <div
                      key={product.id}
                      className="glass-panel rounded-2xl overflow-hidden hover:shadow-xl transition-all duration-300 flex flex-col justify-between border border-slate-200/90 group"
                    >
                      <div>
                        {/* Image & Badges */}
                        <div 
                          onClick={() => openProductDetail(product)}
                          className="h-52 w-full bg-slate-900 relative overflow-hidden cursor-pointer group/img"
                        >
                          <img
                            src={product.image_url}
                            alt={product.title}
                            className="w-full h-full object-cover group-hover/img:scale-105 transition duration-500"
                          />
                          {/* Hover Overlay: Quick View */}
                          <div className="absolute inset-0 bg-slate-950/40 opacity-0 group-hover/img:opacity-100 transition-opacity duration-300 flex items-center justify-center backdrop-blur-[2px]">
                            <span className="px-3.5 py-1.5 rounded-xl bg-white/95 text-slate-900 text-xs font-bold shadow-lg flex items-center space-x-1.5 transform translate-y-2 group-hover/img:translate-y-0 transition duration-300">
                              <span>👁️</span>
                              <span>View Details</span>
                            </span>
                          </div>

                          <div className="absolute top-3 left-3">
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-slate-900/80 text-white backdrop-blur">
                              SKU: {product.sku}
                            </span>
                          </div>
                          <div className="absolute top-3 right-3">
                            {isOutOfStock ? (
                              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-red-600 text-white shadow">
                                Out of Stock
                              </span>
                            ) : isLowStock ? (
                              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-amber-500 text-slate-950 shadow animate-pulse">
                                Only 1 Left!
                              </span>
                            ) : (
                              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-emerald-600 text-white shadow">
                                In Stock ({product.stock})
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Product Info */}
                        <div className="p-5">
                          <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-600 block mb-1">
                            {product.category}
                          </span>
                          <h2 
                            onClick={() => openProductDetail(product)}
                            className="text-base font-bold text-slate-900 mb-2 leading-tight cursor-pointer hover:text-emerald-600 transition"
                            title="Click to view details & specifications"
                          >
                            {product.title}
                          </h2>
                          <p 
                            onClick={() => openProductDetail(product)}
                            className="text-slate-600 text-xs line-clamp-3 leading-relaxed mb-4 cursor-pointer hover:text-slate-900 transition"
                          >
                            {product.description}
                          </p>
                        </div>
                      </div>

                      {/* Action Bar */}
                      <div className="p-5 pt-0">
                        <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                          <div>
                            <div className="text-[10px] text-slate-400 uppercase font-semibold">Price</div>
                            <div className="text-xl font-extrabold text-slate-900">${product.price}</div>
                          </div>

                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => openProductDetail(product)}
                              className="px-3 py-2 rounded-xl text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition flex items-center space-x-1 shadow-sm"
                              title="Inspect product details and choose quantity"
                            >
                              <span>👁️</span>
                              <span>Details</span>
                            </button>

                            <button
                              onClick={() => handleAddToCart(product, 1)}
                              disabled={isOutOfStock}
                              className={`px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 shadow ${isOutOfStock ? 'bg-slate-200 text-slate-400 cursor-not-allowed' : 'bg-emerald-600 hover:bg-emerald-500 text-white'}`}
                              title={isOutOfStock ? 'Sold out' : 'Add 1 to Cart'}
                            >
                              <span>🛒</span>
                              <span>{isOutOfStock ? 'Unavailable' : 'Add'}</span>
                            </button>
                          </div>
                        </div>

                        {/* Admin Stock Replenishment Quick Editor */}
                        {currentUser?.role === 'admin' && (
                          <div className="mt-3 pt-2 border-t border-dashed border-slate-200 text-xs flex items-center justify-between text-slate-600">
                            <span className="font-semibold text-indigo-700">Admin Control:</span>
                            {editingStockId === product.id ? (
                              <div className="flex items-center space-x-1.5">
                                <input
                                  type="number"
                                  min="0"
                                  value={newStockVal}
                                  onChange={(e) => setNewStockVal(parseInt(e.target.value) || 0)}
                                  className="w-16 p-1 text-xs border rounded"
                                />
                                <button
                                  onClick={() => handleSaveStockUpdate(product.id)}
                                  className="bg-indigo-600 text-white px-2 py-1 rounded text-[11px] font-bold"
                                >
                                  Save
                                </button>
                                <button
                                  onClick={() => setEditingStockId(null)}
                                  className="text-slate-400 text-xs"
                                >
                                  ✕
                                </button>
                              </div>
                            ) : (
                              <button
                                onClick={() => { setEditingStockId(product.id); setNewStockVal(product.stock); }}
                                className="text-indigo-600 hover:underline font-bold text-[11px]"
                              >
                                Edit Stock ({product.stock})
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ) : (
          /* Order History View */
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-extrabold text-slate-900">
                  {currentUser?.role === 'admin' ? 'Store Order Management & Fulfillment' : 'Your Order History & Receipts'}
                </h2>
                <p className="text-xs text-slate-500">
                  Unit prices are frozen snapshots locked at purchase time.
                </p>
              </div>
              <button
                onClick={() => setActiveTab('catalog')}
                className="bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-md transition flex items-center space-x-1.5"
              >
                <span>←</span>
                <span>Back to Store Catalog (6 Items)</span>
              </button>
            </div>

            {orders.length === 0 ? (
              <div className="text-center py-16 bg-white rounded-2xl border border-slate-200 p-8">
                <span className="text-4xl mb-3 block">🧾</span>
                <h3 className="text-base font-bold text-slate-800">No orders recorded yet</h3>
                <p className="text-slate-500 text-xs mt-1">Add items to your cart and complete checkout to generate an order receipt.</p>
              </div>
            ) : (
              orders.map((order) => {
                const statusColors: Record<string, string> = {
                  pending: 'bg-amber-100 text-amber-800 border-amber-300',
                  paid: 'bg-emerald-100 text-emerald-800 border-emerald-300',
                  processing: 'bg-sky-100 text-sky-800 border-sky-300',
                  shipped: 'bg-indigo-100 text-indigo-800 border-indigo-300',
                  delivered: 'bg-teal-100 text-teal-800 border-teal-300',
                  cancelled: 'bg-red-100 text-red-800 border-red-300',
                };

                const validNextTransitions: Record<string, string[]> = {
                  pending: ['paid', 'cancelled'],
                  paid: ['processing', 'cancelled'],
                  processing: ['shipped', 'cancelled'],
                  shipped: ['delivered'],
                  delivered: [],
                  cancelled: [],
                };

                const isTerminalState = order.status === 'delivered' || order.status === 'cancelled';
                const nextOptions = validNextTransitions[order.status] || [];

                return (
                  <div key={order.id} className="bg-white rounded-2xl p-6 shadow-md border border-slate-200">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-200 gap-2">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-extrabold text-sm text-slate-900">{order.order_number}</span>
                          <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase border ${statusColors[order.status] || 'bg-slate-100 text-slate-800'}`}>
                            {order.status}
                          </span>
                        </div>
                        <div className="text-xs text-slate-500 mt-0.5">
                          Ordered on {new Date(order.created_at).toLocaleString()} by @{order.user.username}
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="text-xs text-slate-500">Order Total</div>
                        <div className="text-lg font-black text-slate-900">${order.total_amount}</div>
                      </div>
                    </div>

                    {/* Line items table */}
                    <div className="overflow-x-auto mb-4">
                      <table className="w-full text-xs text-left">
                        <thead className="bg-slate-50 text-slate-600 font-semibold uppercase">
                          <tr>
                            <th className="py-2 px-3">Item Description</th>
                            <th className="py-2 px-3 text-center">Frozen Unit Price</th>
                            <th className="py-2 px-3 text-center">Qty</th>
                            <th className="py-2 px-3 text-right">Subtotal</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {order.items.map((item) => (
                            <tr key={item.id}>
                              <td className="py-2.5 px-3 font-medium text-slate-800">{item.product_title}</td>
                              <td className="py-2.5 px-3 text-center text-slate-600">${item.unit_price}</td>
                              <td className="py-2.5 px-3 text-center font-bold text-slate-800">{item.quantity}</td>
                              <td className="py-2.5 px-3 text-right font-bold text-slate-900">${item.subtotal}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Footer & State Transition Guard */}
                    <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between text-xs text-slate-500 gap-2">
                      <div>
                        <span className="font-semibold text-slate-700">Delivery Address:</span> {order.shipping_address}
                        {order.payment_transaction && (
                          <div className="text-[11px] text-slate-400 mt-0.5">
                            Audit Idempotency Key: <code className="bg-slate-100 px-1 py-0.5 rounded">{order.payment_transaction.idempotency_key}</code>
                          </div>
                        )}
                      </div>

                      {/* Admin State Transition Controller */}
                      {currentUser?.role === 'admin' && (
                        <div className="flex items-center space-x-2">
                          <span className="font-bold text-indigo-700 text-[11px]">Transition Order:</span>
                          {isTerminalState ? (
                            <span className="px-2.5 py-1 text-xs rounded-md bg-slate-100 text-slate-600 font-bold border border-slate-300">
                              🔒 Terminal State ({order.status.toUpperCase()})
                            </span>
                          ) : (
                            <select
                              value={order.status}
                              onChange={(e) => handleUpdateOrderStatus(order.id, e.target.value)}
                              className="p-1 text-xs border rounded bg-white text-slate-800 font-semibold focus:outline-none focus:ring-1 focus:ring-indigo-500"
                            >
                              <option value={order.status} disabled>Current: {order.status}</option>
                              {nextOptions.map((nextStatus) => (
                                <option key={nextStatus} value={nextStatus}>
                                  ➔ Advance to: {nextStatus}
                                </option>
                              ))}
                            </select>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </main>

      {/* Shopping Cart Slide-over / Modal */}
      {isCartOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex justify-end">
          <div className="bg-white w-full max-w-md h-full shadow-2xl flex flex-col justify-between p-6">
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-slate-200">
                <div className="flex items-center space-x-2">
                  <span className="text-xl">🛒</span>
                  <h2 className="text-base font-extrabold text-slate-900">Your Shopping Cart</h2>
                </div>
                <button onClick={() => setIsCartOpen(false)} className="text-slate-400 hover:text-slate-600 font-bold">
                  ✕
                </button>
              </div>

              {/* Items List */}
              <div className="mt-4 space-y-3 overflow-y-auto max-h-[60vh] pr-1">
                {!cart || cart.items.length === 0 ? (
                  <div className="text-center py-16 text-slate-400 text-xs">
                    Your cart is currently empty.
                  </div>
                ) : (
                  cart.items.map((item) => (
                    <div key={item.id} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs flex items-center justify-between">
                      <div className="flex-1 pr-2">
                        <div className="font-bold text-slate-800 line-clamp-1">{item.product.title}</div>
                        <div className="text-slate-500 text-[11px]">${item.product.price} each</div>
                        <div className="text-[10px] text-emerald-600">Stock available: {item.product.stock}</div>
                      </div>

                      <div className="flex items-center space-x-2">
                        <div className="flex items-center border border-slate-300 rounded-lg bg-white overflow-hidden">
                          <button
                            onClick={() => handleUpdateCartQty(item.id, item.quantity - 1)}
                            className="px-2 py-0.5 hover:bg-slate-100 font-bold text-slate-600"
                          >
                            -
                          </button>
                          <span className="px-2 font-bold text-slate-900 text-xs">{item.quantity}</span>
                          <button
                            onClick={() => handleUpdateCartQty(item.id, item.quantity + 1)}
                            disabled={item.quantity >= item.product.stock}
                            className={`px-2 py-0.5 font-bold ${item.quantity >= item.product.stock ? 'text-slate-300 cursor-not-allowed' : 'hover:bg-slate-100 text-slate-600'}`}
                          >
                            +
                          </button>
                        </div>
                        <div className="font-black text-slate-900 text-right w-14">
                          ${item.subtotal}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Cart Footer */}
            {cart && cart.items.length > 0 && (
              <div className="pt-4 border-t border-slate-200">
                {!currentUser && (
                  <div className="mb-3 p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs">
                    <div className="font-bold flex items-center space-x-1.5 mb-1">
                      <span>👀</span>
                      <span>Guest Shopping Session</span>
                    </div>
                    <p className="text-[11px] text-amber-800 leading-tight mb-2">
                      Items saved in guest cart! To checkout and reserve stock, choose an account:
                    </p>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => {
                          switchDemoUser('talha_customer', 'Customer@123');
                          showToast('Switched to @talha_customer! Proceed to checkout.');
                        }}
                        className="py-1.5 px-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[11px] shadow text-center"
                      >
                        🛒 As Talha
                      </button>
                      <button
                        onClick={() => {
                          switchDemoUser('alice_buyer', 'Password@123');
                          showToast('Switched to @alice_buyer! Proceed to checkout.');
                        }}
                        className="py-1.5 px-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-bold text-[11px] shadow text-center"
                      >
                        🛒 As Alice
                      </button>
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs text-slate-500">Cart Total ({cart.total_items} items)</span>
                  <span className="text-xl font-extrabold text-slate-900">${cart.total_amount}</span>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleClearCart}
                    className="w-1/3 py-2.5 rounded-xl border border-slate-300 text-slate-600 text-xs font-bold hover:bg-slate-50 transition"
                  >
                    Clear
                  </button>
                  <button
                    onClick={() => {
                      if (!currentUser) {
                        showToast('Please select a customer account (Talha or Alice) to checkout.', true);
                        setIsAuthOpen(true);
                        return;
                      }
                      setIsCartOpen(false);
                      setIsCheckoutOpen(true);
                    }}
                    className="w-2/3 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg transition"
                  >
                    {currentUser ? 'Proceed to Checkout →' : 'Sign In to Checkout →'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Mock Checkout Modal */}
      {isCheckoutOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-200">
              <h3 className="font-extrabold text-slate-900 text-base">
                Mock Payment Checkout
              </h3>
              <button
                onClick={() => { setIsCheckoutOpen(false); setCheckoutError(''); }}
                className="text-slate-400 hover:text-slate-600 font-bold p-1"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleExecuteCheckout} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Shipping Address *</label>
                <textarea
                  value={shippingAddress}
                  onChange={(e) => setShippingAddress(e.target.value)}
                  rows={2}
                  className="w-full p-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-500"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Simulated Card Payment Token</label>
                <select
                  value={paymentToken}
                  onChange={(e) => { setPaymentToken(e.target.value); setCheckoutError(''); }}
                  className="w-full p-2.5 rounded-lg border border-slate-300 bg-white font-medium"
                >
                  <option value="tok_success">🟢 tok_success — Visa / MC (Succeed & Charge)</option>
                  <option value="tok_decline">🔴 tok_decline — Insufficient Funds (Decline)</option>
                  <option value="tok_invalid_cvv">🔴 tok_invalid_cvv — Bad CVV (Security Reject)</option>
                  <option value="tok_expired_card">🔴 tok_expired_card — Expired Card</option>
                  <option value="tok_gateway_timeout">🟡 tok_gateway_timeout — Bank Gateway Error</option>
                </select>
                <p className="text-[10px] text-slate-400 mt-1">
                  * Mock environment: No real credit cards or financial transactions occur.
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <div className="flex justify-between text-slate-600 mb-1">
                  <span>Subtotal</span>
                  <span>${cart?.total_amount}</span>
                </div>
                <div className="flex justify-between text-slate-600 mb-1">
                  <span>Standard Shipping</span>
                  <span className="text-emerald-600 font-bold">FREE</span>
                </div>
                <div className="flex justify-between font-extrabold text-slate-900 text-sm pt-2 border-t border-slate-200">
                  <span>Total Amount</span>
                  <span>${cart?.total_amount}</span>
                </div>
              </div>

              {/* In-Modal Clear Error Banner */}
              {checkoutError && (
                <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-medium flex items-start space-x-2.5 animate-fade-in">
                  <span className="text-base leading-none mt-0.5">⚠️</span>
                  <div>
                    <div className="font-bold text-red-800">Card Payment Declined</div>
                    <div className="text-[11px] mt-0.5 text-red-600">{checkoutError}</div>
                    <div className="text-[10px] mt-1 text-slate-500 font-normal">
                      Stock is fully preserved. Please switch token to <strong>tok_success</strong> to complete order.
                    </div>
                  </div>
                </div>
              )}

              <button
                type="submit"
                disabled={isProcessingCheckout}
                className={`w-full py-3 rounded-xl text-white text-xs font-black shadow-lg transition ${isProcessingCheckout ? 'bg-slate-400 cursor-wait' : 'bg-emerald-600 hover:bg-emerald-500'}`}
              >
                {isProcessingCheckout ? 'Simulating Card Processing...' : `Authorize & Pay $${cart?.total_amount}`}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Auth Modal */}
      {isAuthOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full shadow-2xl border border-slate-200 p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-200">
              <h3 className="font-bold text-slate-900 text-sm">
                {authMode === 'login' ? 'Customer Sign In' : 'Create Customer Account'}
              </h3>
              <button onClick={() => setIsAuthOpen(false)} className="text-slate-400 font-bold">✕</button>
            </div>

            <form
              onSubmit={async (e) => {
                e.preventDefault();
                try {
                  if (authMode === 'login') {
                    await api.login({ username: authUsername, password: authPassword });
                  } else {
                    await api.register({ username: authUsername, password: authPassword, role: authRole });
                    await api.login({ username: authUsername, password: authPassword });
                  }
                  setCurrentUser(api.getCurrentUser());
                  setIsAuthOpen(false);
                  showToast('Authentication successful!');
                  loadCart();
                  loadOrders();
                  loadProducts();
                } catch (err: any) {
                  showToast(err.message, true);
                }
              }}
              className="space-y-3 text-xs"
            >
              <div>
                <label className="block font-bold text-slate-700 mb-1">Username</label>
                <input
                  type="text"
                  value={authUsername}
                  onChange={(e) => setAuthUsername(e.target.value)}
                  className="w-full p-2 rounded-lg border border-slate-300"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Password</label>
                <input
                  type="password"
                  value={authPassword}
                  onChange={(e) => setAuthPassword(e.target.value)}
                  className="w-full p-2 rounded-lg border border-slate-300"
                  required
                />
              </div>

              {authMode === 'register' && (
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Role</label>
                  <select
                    value={authRole}
                    onChange={(e) => setAuthRole(e.target.value as any)}
                    className="w-full p-2 rounded-lg border border-slate-300 bg-white"
                  >
                    <option value="customer">Customer (Shop & Order)</option>
                    <option value="admin">Store Admin (Fulfillment)</option>
                  </select>
                </div>
              )}

              <button
                type="submit"
                className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2.5 rounded-lg shadow mt-2"
              >
                {authMode === 'login' ? 'Authenticate' : 'Register Account'}
              </button>

              <div className="text-center pt-2 text-[11px] text-slate-500">
                {authMode === 'login' ? (
                  <span>New customer? <button type="button" onClick={() => setAuthMode('register')} className="text-emerald-600 font-bold hover:underline">Register</button></span>
                ) : (
                  <span>Have account? <button type="button" onClick={() => setAuthMode('login')} className="text-emerald-600 font-bold hover:underline">Sign In</button></span>
                )}
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Product Detail / Quick View Modal */}
      {selectedProductDetail && (
        <div className="fixed inset-0 z-50 bg-slate-900/65 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-3xl max-w-3xl w-full shadow-2xl border border-slate-200 overflow-hidden relative my-8 animate-in fade-in zoom-in-95 duration-200">
            {/* Close Button */}
            <button
              onClick={() => setSelectedProductDetail(null)}
              className="absolute top-4 right-4 z-20 w-9 h-9 rounded-full bg-white/90 hover:bg-white text-slate-600 hover:text-slate-950 flex items-center justify-center text-sm font-bold shadow-md border border-slate-200 transition"
              aria-label="Close modal"
            >
              ✕
            </button>

            <div className="grid grid-cols-1 md:grid-cols-2">
              {/* Product Media Column */}
              <div className="bg-slate-950 p-6 flex flex-col justify-between relative min-h-[320px] md:min-h-[460px]">
                <div className="relative w-full h-64 md:h-80 rounded-2xl overflow-hidden bg-slate-900 flex items-center justify-center border border-slate-800">
                  <img
                    src={selectedProductDetail.image_url}
                    alt={selectedProductDetail.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-3 left-3">
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-slate-900/80 text-white backdrop-blur border border-white/10">
                      SKU: {selectedProductDetail.sku}
                    </span>
                  </div>
                  <div className="absolute top-3 right-3">
                    {selectedProductDetail.stock <= 0 ? (
                      <span className="px-2.5 py-1 rounded-full text-[10px] font-black uppercase bg-red-600 text-white shadow">
                        Out of Stock
                      </span>
                    ) : selectedProductDetail.stock === 1 ? (
                      <span className="px-2.5 py-1 rounded-full text-[10px] font-black uppercase bg-amber-500 text-slate-950 shadow animate-pulse">
                        Only 1 Left!
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 rounded-full text-[10px] font-black uppercase bg-emerald-600 text-white shadow">
                        In Stock ({selectedProductDetail.stock})
                      </span>
                    )}
                  </div>
                </div>

                {/* Trust Badges */}
                <div className="mt-4 pt-4 border-t border-slate-800/80 grid grid-cols-3 gap-2 text-center text-[10px] text-slate-300">
                  <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
                    <div className="text-base mb-0.5">⚡</div>
                    <div className="font-bold">Fast Dispatch</div>
                    <div className="text-slate-400 text-[9px]">Priority Cargo</div>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
                    <div className="text-base mb-0.5">🛡️</div>
                    <div className="font-bold">Authentic</div>
                    <div className="text-slate-400 text-[9px]">100% Genuine</div>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
                    <div className="text-base mb-0.5">🔒</div>
                    <div className="font-bold">ACID Safe</div>
                    <div className="text-slate-400 text-[9px]">Pessimistic Lock</div>
                  </div>
                </div>
              </div>

              {/* Product Info & Purchase Controls Column */}
              <div className="p-6 md:p-8 flex flex-col justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-emerald-100 text-emerald-800">
                      {selectedProductDetail.category}
                    </span>
                    <span className="text-xs text-slate-400">•</span>
                    <span className="text-xs font-medium text-slate-400">NovaMart Store</span>
                  </div>

                  <h2 className="text-xl sm:text-2xl font-black text-slate-900 mb-2 leading-snug">
                    {selectedProductDetail.title}
                  </h2>

                  {/* Price Banner */}
                  <div className="flex items-baseline space-x-3 mb-4 pb-4 border-b border-slate-100">
                    <span className="text-3xl font-black text-slate-900">
                      ${selectedProductDetail.price}
                    </span>
                    <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                      Free Shipping Included
                    </span>
                  </div>

                  {/* Stock Status Notice */}
                  <div className="mb-4">
                    {selectedProductDetail.stock <= 0 ? (
                      <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center space-x-2">
                        <span>🔴</span>
                        <span className="font-medium">Currently out of stock. Backorder replenishment is in progress.</span>
                      </div>
                    ) : selectedProductDetail.stock === 1 ? (
                      <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center space-x-2 animate-pulse">
                        <span>⚠️</span>
                        <span className="font-semibold">Urgent: Only 1 unit left in live inventory!</span>
                      </div>
                    ) : (
                      <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-center space-x-2">
                        <span>🟢</span>
                        <span><strong>{selectedProductDetail.stock} units ready in warehouse.</strong> Real-time row-locking protects your order.</span>
                      </div>
                    )}
                  </div>

                  {/* Full Description */}
                  <div className="mb-6">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                      Overview & Specifications
                    </h3>
                    <p className="text-slate-600 text-xs sm:text-sm leading-relaxed whitespace-pre-line">
                      {selectedProductDetail.description}
                    </p>
                  </div>
                </div>

                {/* Bottom Interactive Area: Quantity Selector & Add to Cart */}
                <div className="pt-4 border-t border-slate-200 space-y-4">
                  {selectedProductDetail.stock > 0 ? (
                    <>
                      {/* Quantity Selector */}
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-xs font-bold text-slate-800">Quantity</div>
                          <div className="text-[11px] text-slate-400">
                            Subtotal: <strong className="text-slate-900">${(parseFloat(selectedProductDetail.price) * detailQty).toFixed(2)}</strong>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-xl border border-slate-200">
                          <button
                            type="button"
                            onClick={() => setDetailQty((prev) => Math.max(1, prev - 1))}
                            disabled={detailQty <= 1}
                            className={`w-8 h-8 rounded-lg font-bold text-sm flex items-center justify-center transition ${detailQty <= 1 ? 'text-slate-300 cursor-not-allowed' : 'bg-white hover:bg-slate-200 text-slate-800 shadow-sm'}`}
                          >
                            −
                          </button>
                          <span className="w-10 text-center text-sm font-extrabold text-slate-900">
                            {detailQty}
                          </span>
                          <button
                            type="button"
                            onClick={() => setDetailQty((prev) => Math.min(selectedProductDetail.stock, prev + 1))}
                            disabled={detailQty >= selectedProductDetail.stock}
                            className={`w-8 h-8 rounded-lg font-bold text-sm flex items-center justify-center transition ${detailQty >= selectedProductDetail.stock ? 'text-slate-300 cursor-not-allowed' : 'bg-white hover:bg-slate-200 text-slate-800 shadow-sm'}`}
                          >
                            +
                          </button>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="grid grid-cols-2 gap-3">
                        <button
                          type="button"
                          onClick={() => {
                            handleAddToCart(selectedProductDetail, detailQty);
                            setSelectedProductDetail(null);
                          }}
                          className="w-full py-3 px-4 rounded-xl font-bold text-xs bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg transition flex items-center justify-center space-x-2"
                        >
                          <span>🛒</span>
                          <span>Add to Cart ({detailQty})</span>
                        </button>

                        <button
                          type="button"
                          onClick={() => handleBuyNowFromModal(selectedProductDetail, detailQty)}
                          className="w-full py-3 px-4 rounded-xl font-bold text-xs bg-slate-900 hover:bg-slate-800 text-white shadow-lg transition flex items-center justify-center space-x-2"
                        >
                          <span>⚡</span>
                          <span>Buy Now</span>
                        </button>
                      </div>
                    </>
                  ) : (
                    <button
                      disabled
                      className="w-full py-3 px-4 rounded-xl font-bold text-xs bg-slate-200 text-slate-400 cursor-not-allowed flex items-center justify-center space-x-2"
                    >
                      <span>🚫</span>
                      <span>Item Out of Stock</span>
                    </button>
                  )}

                  {/* Admin stock inline editor inside modal */}
                  {currentUser?.role === 'admin' && (
                    <div className="p-3 rounded-xl bg-indigo-50 border border-indigo-200 text-xs flex items-center justify-between">
                      <span className="font-bold text-indigo-900">Admin Inventory Adjust:</span>
                      <div className="flex items-center space-x-1.5">
                        <input
                          type="number"
                          min="0"
                          defaultValue={selectedProductDetail.stock}
                          id="modal-admin-stock-input"
                          className="w-16 p-1 text-xs border rounded bg-white text-slate-900"
                        />
                        <button
                          onClick={async () => {
                            const input = document.getElementById('modal-admin-stock-input') as HTMLInputElement;
                            const val = parseInt(input?.value) || 0;
                            try {
                              await api.updateStock(selectedProductDetail.id, val);
                              showToast(`Stock updated to ${val} units!`);
                              setSelectedProductDetail({
                                ...selectedProductDetail,
                                stock: val
                              });
                              loadProducts();
                            } catch (err: any) {
                              showToast(err.message, true);
                            }
                          }}
                          className="bg-indigo-600 hover:bg-indigo-500 text-white px-2.5 py-1 rounded text-[11px] font-bold shadow"
                        >
                          Update
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Clean Minimalist Footer */}
      <footer className="border-t border-slate-200 bg-white/80 backdrop-blur py-6 mt-16 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 rounded-lg bg-slate-900 text-white font-black text-xs flex items-center justify-center">
              NM
            </div>
            <span className="font-bold text-slate-800 text-sm tracking-tight">NovaMart</span>
            <span className="text-slate-300">•</span>
            <span className="text-slate-500">High-Integrity Commerce Platform</span>
          </div>

          <div className="flex items-center space-x-1.5 text-slate-600">
            <span>Crafted & Engineered by</span>
            <span className="font-bold text-slate-900 px-2.5 py-0.5 bg-slate-100 rounded-md border border-slate-200">
              Talha Ahmed
            </span>
          </div>

          <div className="flex items-center space-x-4 text-[11px] text-slate-400">
            <span className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              <span>PostgreSQL 18</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-sky-500"></span>
              <span>Django DRF</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
              <span>Next.js 14</span>
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
