"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import ApiClient from "@/lib/api-client"
import { useRouter } from "next/navigation"
import { toast } from "@/components/ui/use-toast"

interface AuthContextType {
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  register: (username: string, email: string, password: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const router = useRouter()
  const apiClient = new ApiClient()

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem("auth_token")
    setIsAuthenticated(!!token)
    setIsLoading(false)
  }, [])

  const login = async (username: string, password: string) => {
    try {
      setIsLoading(true)
      await apiClient.login(username, password)
      setIsAuthenticated(true)
      toast({
        title: "Login successful",
        description: "Welcome back!",
      })
      router.push("/")
    } catch (error) {
      console.error("Login error:", error)
      setIsAuthenticated(false)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    apiClient.logout()
    setIsAuthenticated(false)
    router.push("/login")
    toast({
      title: "Logged out",
      description: "You have been logged out successfully.",
    })
  }

  const register = async (username: string, email: string, password: string) => {
    try {
      setIsLoading(true)
      await apiClient.register(username, email, password)
      toast({
        title: "Registration successful",
        description: "Please log in with your new account.",
      })
      router.push("/login")
    } catch (error) {
      console.error("Registration error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
