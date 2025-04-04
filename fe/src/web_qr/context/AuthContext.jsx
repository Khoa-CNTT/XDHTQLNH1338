import { createContext, useState, useEffect, useContext } from 'react'
import {
  loginAccount,
  readSession,
} from '../services/api.jsx'

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const fetchSession = await readSession()
        if (fetchSession.status === 200) {
          setUser(fetchSession?.data?.session?.status)
        } else {
          setUser(null)
        }
      } catch (error) {
        setUser(null)
      }
    }
    fetchUserProfile()
  }, [])

  const login = async (data) => {
    try {
      let res = await loginAccount(data);
      return res;
    } catch (error) {
      return error
    }
  };

  return (
    <AuthContext.Provider value={{ user, login }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
