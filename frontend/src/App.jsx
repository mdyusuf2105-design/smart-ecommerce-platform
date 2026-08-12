import { useEffect, useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import './App.css'

function App() {
  const {
    isLoading,
    isAuthenticated,
    user,
    loginWithRedirect,
    logout,
    getAccessTokenSilently,
  } = useAuth0()

  const [products, setProducts] = useState([])

  const [cart, setCart] = useState(() => {
    try {
      const savedCart = localStorage.getItem('cart')
      return savedCart ? JSON.parse(savedCart) : []
    } catch {
      return []
    }
  })

  const [showCart, setShowCart] = useState(false)
  const [loadingProducts, setLoadingProducts] = useState(false)
  const [error, setError] = useState('')

  // --------------------------------------------------
  // SAVE CART
  // --------------------------------------------------

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart))
  }, [cart])

  // --------------------------------------------------
  // AUTH0 -> FASTAPI JWT
  // --------------------------------------------------

  const authenticateWithBackend = async () => {
    try {
      const auth0Token = await getAccessTokenSilently({
        authorizationParams: {
          audience: import.meta.env.VITE_AUTH0_AUDIENCE,
        },
      })

      console.log('Auth0 token received:', !!auth0Token)

      const response = await fetch(
        'http://localhost:8000/auth/auth0',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            token: auth0Token,
          }),
        }
      )

      const responseText = await response.text()

      console.log(
        'FastAPI Auth0 status:',
        response.status
      )

      if (!response.ok) {
        console.error(
          'FastAPI Auth0 response:',
          responseText
        )

        throw new Error(
          `Backend returned ${response.status}: ${responseText}`
        )
      }

      const data = JSON.parse(responseText)

      if (data.access_token) {
        localStorage.setItem(
          'access_token',
          data.access_token
        )
      }

      if (data.refresh_token) {
        localStorage.setItem(
          'refresh_token',
          data.refresh_token
        )
      }

      console.log(
        'FastAPI JWT authentication successful'
      )

      return data.access_token
    } catch (err) {
      console.error(
        'Backend authentication error:',
        err
      )

      /*
        We don't stop the frontend here.

        Products are still loaded from the working
        FastAPI /products/ endpoint.
      */

      return null
    }
  }

  // --------------------------------------------------
  // LOAD PRODUCTS AFTER LOGIN
  // --------------------------------------------------

  useEffect(() => {
    if (isAuthenticated) {
      authenticateWithBackend()
      fetchProducts()
    }
  }, [isAuthenticated])

  // --------------------------------------------------
  // FETCH PRODUCTS
  // --------------------------------------------------

  const fetchProducts = async () => {
    try {
      setLoadingProducts(true)
      setError('')

      const response = await fetch(
        'http://localhost:8000/products/'
      )

      if (!response.ok) {
        throw new Error(
          `Failed to fetch products: ${response.status}`
        )
      }

      const data = await response.json()

      setProducts(
        Array.isArray(data)
          ? data
          : data.products || []
      )
    } catch (err) {
      console.error('Product error:', err)
      setError('Unable to load products')
    } finally {
      setLoadingProducts(false)
    }
  }

  // --------------------------------------------------
  // ADD TO CART
  // --------------------------------------------------

  const addToCart = (product) => {
    setCart((currentCart) => {
      const existing = currentCart.find(
        (item) => item.id === product.id
      )

      if (existing) {
        return currentCart.map((item) =>
          item.id === product.id
            ? {
                ...item,
                quantity: item.quantity + 1,
              }
            : item
        )
      }

      return [
        ...currentCart,
        {
          ...product,
          quantity: 1,
        },
      ]
    })
  }

  // --------------------------------------------------
  // INCREASE QUANTITY
  // --------------------------------------------------

  const increaseQuantity = (id) => {
    setCart((currentCart) =>
      currentCart.map((item) =>
        item.id === id
          ? {
              ...item,
              quantity: item.quantity + 1,
            }
          : item
      )
    )
  }

  // --------------------------------------------------
  // DECREASE QUANTITY
  // --------------------------------------------------

  const decreaseQuantity = (id) => {
    setCart((currentCart) =>
      currentCart
        .map((item) =>
          item.id === id
            ? {
                ...item,
                quantity: item.quantity - 1,
              }
            : item
        )
        .filter((item) => item.quantity > 0)
    )
  }

  // --------------------------------------------------
  // REMOVE FROM CART
  // --------------------------------------------------

  const removeFromCart = (id) => {
    setCart((currentCart) =>
      currentCart.filter(
        (item) => item.id !== id
      )
    )
  }

  // --------------------------------------------------
  // CART TOTAL
  // --------------------------------------------------

  const total = cart.reduce(
    (sum, item) =>
      sum +
      Number(item.price || 0) *
        item.quantity,
    0
  )

  // --------------------------------------------------
  // CART COUNT
  // --------------------------------------------------

  const cartCount = cart.reduce(
    (sum, item) =>
      sum + item.quantity,
    0
  )

  // --------------------------------------------------
  // LOADING
  // --------------------------------------------------

  if (isLoading) {
    return (
      <div className="loading">
        Loading...
      </div>
    )
  }

  // --------------------------------------------------
  // LOGIN PAGE
  // --------------------------------------------------

  if (!isAuthenticated) {
    return (
      <div className="login-page">
        <div className="login-card">

          <h1>
            Smart E-Commerce Platform
          </h1>

          <p>
            Sign in to continue
          </p>

          <button
            className="login-button"
            onClick={() =>
              loginWithRedirect({
                authorizationParams: {
                  connection:
                    'google-oauth2',
                  audience:
                    import.meta.env
                      .VITE_AUTH0_AUDIENCE,
                },
              })
            }
          >
            Continue with Google
          </button>

          <button
            className="login-button"
            onClick={() =>
              loginWithRedirect({
                authorizationParams: {
                  connection:
                    'facebook',
                  audience:
                    import.meta.env
                      .VITE_AUTH0_AUDIENCE,
                },
              })
            }
          >
            Continue with Facebook
          </button>

        </div>
      </div>
    )
  }

  // --------------------------------------------------
  // MAIN APPLICATION
  // --------------------------------------------------

  return (
    <div className="app">

      {/* NAVBAR */}

      <nav className="navbar">

        <h2>
          Smart E-Commerce
        </h2>

        <div className="nav-right">

          <button
            className="cart-button"
            onClick={() =>
              setShowCart(!showCart)
            }
          >
            🛒 Cart ({cartCount})
          </button>

          <span>
            {user?.name || 'Customer'}
          </span>

          <button
            onClick={() =>
              logout({
                logoutParams: {
                  returnTo:
                    window.location.origin,
                },
              })
            }
          >
            Logout
          </button>

        </div>

      </nav>

      {/* CART */}

      {showCart ? (

        <main className="cart-page">

          <div className="section-header">

            <h1>
              Your Cart 🛒
            </h1>

            <button
              onClick={() =>
                setShowCart(false)
              }
            >
              Continue Shopping
            </button>

          </div>

          {cart.length === 0 ? (

            <div className="empty-cart">

              <h2>
                Your cart is empty
              </h2>

              <p>
                Add some products to get
                started.
              </p>

              <button
                onClick={() =>
                  setShowCart(false)
                }
              >
                Browse Products
              </button>

            </div>

          ) : (

            <div className="cart-container">

              <div className="cart-items">

                {cart.map((item) => (

                  <div
                    className="cart-item"
                    key={item.id}
                  >

                    <div className="cart-item-info">

                      <h3>
                        {item.name}
                      </h3>

                      <p>
                        ₹
                        {Number(
                          item.price || 0
                        )}
                      </p>

                    </div>

                    <div className="quantity-controls">

                      <button
                        onClick={() =>
                          decreaseQuantity(
                            item.id
                          )
                        }
                      >
                        −
                      </button>

                      <span>
                        {item.quantity}
                      </span>

                      <button
                        onClick={() =>
                          increaseQuantity(
                            item.id
                          )
                        }
                      >
                        +
                      </button>

                    </div>

                    <strong>
                      ₹
                      {(
                        Number(
                          item.price || 0
                        ) *
                        item.quantity
                      ).toFixed(2)}
                    </strong>

                    <button
                      className="remove-button"
                      onClick={() =>
                        removeFromCart(
                          item.id
                        )
                      }
                    >
                      Remove
                    </button>

                  </div>

                ))}

              </div>

              {/* ORDER SUMMARY */}

              <div className="cart-summary">

                <h2>
                  Order Summary
                </h2>

                <div className="summary-row">

                  <span>
                    Items
                  </span>

                  <span>
                    {cartCount}
                  </span>

                </div>

                <div className="summary-row total-row">

                  <strong>
                    Total
                  </strong>

                  <strong>
                    ₹{total.toFixed(2)}
                  </strong>

                </div>

                <button
                  className="checkout-button"
                >
                  Proceed to Checkout
                </button>

              </div>

            </div>

          )}

        </main>

      ) : (

        /* PRODUCTS */

        <main className="main-content">

          {/* WELCOME */}

          <section className="welcome">

            <div>

              <h1>
                Welcome,{' '}
                {user?.name ||
                  'Customer'} 👋
              </h1>

              <p>
                Discover our products
                and shop with ease.
              </p>

            </div>

            {user?.picture && (
              <img
                src={user.picture}
                alt="Profile"
                className="profile-image"
              />
            )}

          </section>

          {/* PRODUCTS */}

          <section className="products-section">

            <div className="section-header">

              <h2>
                Products
              </h2>

              <button
                onClick={fetchProducts}
              >
                Refresh
              </button>

            </div>

            {loadingProducts && (
              <p className="message">
                Loading products...
              </p>
            )}

            {error && (
              <p className="error">
                {error}
              </p>
            )}

            <div className="product-grid">

              {products.map(
                (product) => (

                  <div
                    className="product-card"
                    key={product.id}
                  >

                    <div className="product-image">

                      {product.images ? (

                        <img
                          src={
                            Array.isArray(
                              product.images
                            )
                              ? product
                                  .images[0]
                              : product.images
                          }
                          alt={
                            product.name
                          }
                          onError={(e) => {
                            e.currentTarget.style.display =
                              'none'
                          }}
                        />

                      ) : (

                        <span>
                          🛍️
                        </span>

                      )}

                    </div>

                    <div className="product-info">

                      <h3>
                        {product.name}
                      </h3>

                      <p>
                        {product.description ||
                          'Quality product'}
                      </p>

                      <div className="product-bottom">

                        <strong>
                          ₹
                          {product.price}
                        </strong>

                        <button
                          onClick={() =>
                            addToCart(
                              product
                            )
                          }
                        >
                          Add to Cart
                        </button>

                      </div>

                    </div>

                  </div>

                )
              )}

            </div>

          </section>

        </main>

      )}

      {/* FOOTER */}

      <footer>
        © 2026 Smart E-Commerce Platform
      </footer>

    </div>
  )
}

export default App