export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8002/api';

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'customer' | 'admin';
  phone?: string;
  address?: string;
}

export interface Product {
  id: number;
  title: string;
  slug: string;
  description: string;
  price: string;
  stock: number;
  in_stock: boolean;
  sku: string;
  category: string;
  image_url: string;
  is_active: boolean;
}

export interface CartItem {
  id: number;
  product: Product;
  quantity: number;
  subtotal: string;
}

export interface Cart {
  id: number;
  items: CartItem[];
  total_amount: string;
  total_items: number;
}

export interface OrderItem {
  id: number;
  product: number;
  product_title: string;
  unit_price: string;
  quantity: number;
  subtotal: string;
}

export interface PaymentTransaction {
  idempotency_key: string;
  amount: string;
  payment_token: string;
  status: 'success' | 'declined' | 'error';
  gateway_message: string;
  created_at: string;
}

export interface Order {
  id: number;
  order_number: string;
  user: User;
  total_amount: string;
  status: 'pending' | 'paid' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  shipping_address: string;
  payment_transaction?: PaymentTransaction;
  items: OrderItem[];
  created_at: string;
}

function getAuthHeader(): Record<string, string> {
  if (typeof window === 'undefined') return {};
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  // Auth
  async login(credentials: { username: string; password: string }) {
    const res = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || data.message || 'Login failed');
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    return data;
  },

  async register(payload: { username: string; email?: string; password: string; role?: string; address?: string }) {
    const res = await fetch(`${API_BASE_URL}/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      const err = Object.values(data).flat().join(', ') || 'Registration failed';
      throw new Error(err);
    }
    return data;
  },

  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  getCurrentUser(): User | null {
    if (typeof window === 'undefined') return null;
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  // Products
  async getProducts(params?: { category?: string; search?: string; in_stock?: boolean }): Promise<Product[]> {
    const query = new URLSearchParams();
    if (params?.category) query.append('category', params.category);
    if (params?.search) query.append('search', params.search);
    if (params?.in_stock) query.append('in_stock', 'true');

    const res = await fetch(`${API_BASE_URL}/products/?${query.toString()}`);
    const data = await res.json();
    return Array.isArray(data) ? data : data.results || [];
  },

  async updateStock(id: number, stock: number, price?: number) {
    const res = await fetch(`${API_BASE_URL}/products/${id}/update_stock/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify({ stock, price }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Failed to update stock');
    return data;
  },

  // Cart
  async getCart(): Promise<Cart> {
    const res = await fetch(`${API_BASE_URL}/cart/`, {
      headers: getAuthHeader(),
    });
    const data = await res.json();
    return data.data;
  },

  async addToCart(productId: number, quantity = 1) {
    const res = await fetch(`${API_BASE_URL}/cart/add/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify({ product_id: productId, quantity }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Failed to add item to cart');
    return data;
  },

  async updateCartItem(itemId: number, quantity: number) {
    const res = await fetch(`${API_BASE_URL}/cart/item/${itemId}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify({ quantity }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Failed to update quantity');
    return data;
  },

  async clearCart() {
    const res = await fetch(`${API_BASE_URL}/cart/clear/`, {
      method: 'POST',
      headers: getAuthHeader(),
    });
    const data = await res.json();
    return data;
  },

  // Checkout & Orders
  async checkout(payload: { payment_token: string; idempotency_key: string; shipping_address?: string }): Promise<Order> {
    const res = await fetch(`${API_BASE_URL}/orders/checkout/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Checkout failed');
    return data.data;
  },

  async getOrders(): Promise<Order[]> {
    const res = await fetch(`${API_BASE_URL}/orders/`, {
      headers: getAuthHeader(),
    });
    const data = await res.json();
    return Array.isArray(data) ? data : data.results || [];
  },

  async updateOrderStatus(orderId: number, status: string): Promise<Order> {
    const res = await fetch(`${API_BASE_URL}/orders/${orderId}/update_status/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify({ status }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.status?.[0] || data.message || 'Invalid status transition');
    return data.data;
  },
};
