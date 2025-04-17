import { toast } from "@/components/ui/use-toast"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface ApiClientOptions {
  token?: string
}

class ApiClient {
  private token: string | null = null

  constructor(options?: ApiClientOptions) {
    if (options?.token) {
      this.token = options.token
    } else if (typeof window !== "undefined") {
      // Try to get token from localStorage in browser environment
      this.token = localStorage.getItem("auth_token")
    }
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    }

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`
    }

    return headers
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = "An error occurred"
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorMessage
      } catch (e) {
        // Ignore JSON parsing errors
      }

      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      })

      throw new Error(errorMessage)
    }

    return response.json()
  }

  async login(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const formData = new URLSearchParams()
    formData.append("username", username)
    formData.append("password", password)

    const response = await fetch(`${API_BASE_URL}/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    })

    const data = await this.handleResponse<{ access_token: string; token_type: string }>(response)
    this.token = data.access_token

    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", data.access_token)
    }

    return data
  }

  async register(username: string, email: string, password: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ username, email, password }),
    })

    return this.handleResponse(response)
  }

  async logout(): Promise<void> {
    this.token = null
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token")
    }
  }

  async getDashboard(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/dashboard`, {
      method: "GET",
      headers: this.getHeaders(),
    })

    return this.handleResponse(response)
  }

  async getOpportunities(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/opportunities`, {
      method: "GET",
      headers: this.getHeaders(),
    })

    return this.handleResponse(response)
  }

  async scanOpportunities(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/opportunities/scan`, {
      method: "POST",
      headers: this.getHeaders(),
    })

    return this.handleResponse(response)
  }

  async executeOpportunity(opportunityId: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/opportunities/execute`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ opportunity_id: opportunityId }),
    })

    return this.handleResponse(response)
  }

  async getTrades(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/trades`, {
      method: "GET",
      headers: this.getHeaders(),
    })

    return this.handleResponse(response)
  }

  async getWallets(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/wallets`, {
      method: "GET",
      headers: this.getHeaders(),
    })

    return this.handleResponse(response)
  }

  async createWallet(walletData: any): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/wallets`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(walletData),
    })

    return this.handleResponse(response)
  }

  async getWalletBalances(walletId: number): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/wallets/${walletId}/balances`, {
      method: "GET",
      headers: this.getHeaders(),
    })

    return this.handleResponse(response)
  }

  async getSettings(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/settings`, {
      method: "GET",
      headers: this.getHeaders(),
    })

    return this.handleResponse(response)
  }

  async updateSettings(category: string, settings: any): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/settings/${category}`, {
      method: "PUT",
      headers: this.getHeaders(),
      body: JSON.stringify({ settings }),
    })

    return this.handleResponse(response)
  }

  async getBotStatus(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/bot/status`, {
      method: "GET",
      headers: this.getHeaders(),
    })

    return this.handleResponse(response)
  }

  async updateBotStatus(active: boolean): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/bot/status`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ active }),
    })

    return this.handleResponse(response)
  }

  async getTradeRisk(opportunityId: number): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/risk/trade/${opportunityId}`, {
      method: "GET",
      headers: this.getHeaders(),
    })

    return this.handleResponse(response)
  }

  async getPortfolioRisk(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/risk/portfolio`, {
      method: "GET",
      headers: this.getHeaders(),
    })

    return this.handleResponse(response)
  }

  async simulateTransaction(opportunityId: number): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/opportunities/${opportunityId}/simulate`, {
      method: "POST",
      headers: this.getHeaders(),
    })

    return this.handleResponse(response)
  }

  async getRealTimePrice(inputMint: string, outputMint: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/prices?inputMint=${inputMint}&outputMint=${outputMint}`, {
      method: "GET",
      headers: this.getHeaders(),
    })

    return this.handleResponse(response)
  }
}

export default ApiClient
