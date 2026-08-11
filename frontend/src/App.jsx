import { useAuth0 } from '@auth0/auth0-react'
import './App.css'

function App() {
  const {
    isLoading,
    isAuthenticated,
    user,
    loginWithRedirect,
    logout,
  } = useAuth0()

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="app">
      <h1>Smart E-Commerce Platform</h1>

      {!isAuthenticated ? (
        <div>
          <p>Sign in to continue</p>

          <button
            onClick={() =>
              loginWithRedirect({
                authorizationParams: {
                  connection: 'google-oauth2',
                },
              })
            }
          >
            Continue with Google
          </button>

          <button
            onClick={() =>
              loginWithRedirect({
                authorizationParams: {
                  connection: 'facebook',
                },
              })
            }
          >
            Continue with Facebook
          </button>
        </div>
      ) : (
        <div>
          <h2>Welcome!</h2>

          {user?.picture && (
            <img
              src={user.picture}
              alt="Profile"
              className="profile-image"
            />
          )}

          <p>{user?.name}</p>
          <p>{user?.email}</p>

          <button
            onClick={() =>
              logout({
                logoutParams: {
                  returnTo: window.location.origin,
                },
              })
            }
          >
            Logout
          </button>
        </div>
      )}
    </div>
  )
}

export default App