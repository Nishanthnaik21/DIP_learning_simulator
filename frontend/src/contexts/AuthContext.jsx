import { createContext, useContext, useState } from 'react'
import { authAPI } from '../utils/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('dip_user')
      return stored ? JSON.parse(stored) : null
    } catch { return null }
  })
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  async function login(email, password) {
    setLoading(true); setError(null)
    try {
      const res = await authAPI.login(email, password)
      const userData = res.data
      setUser(userData)
      localStorage.setItem('dip_user', JSON.stringify(userData))
      return userData
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed. Check your credentials.'
      setError(msg)
      throw new Error(msg)
    } finally {
      setLoading(false)
    }
  }

  async function register(email, password, username = '', role = 'student') {
    setLoading(true); setError(null)
    try {
      const res = await authAPI.register(email, password, username, role)
      return res.data
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed.'
      setError(msg)
      throw new Error(msg)
    } finally {
      setLoading(false)
    }
  }

  function logout() {
    setUser(null)
    localStorage.removeItem('dip_user')
  }

  return (
    <AuthContext.Provider value={{ user, loading, error, login, logout, register, setError }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
