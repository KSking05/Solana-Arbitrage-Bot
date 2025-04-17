"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowUpIcon, ArrowDownIcon } from "@heroicons/react/24/solid"
import { Skeleton } from "@/components/ui/skeleton"

interface PriceData {
  symbol: string
  price: number
  price_change_pct?: number
  last_updated: string
}

interface RealTimePricesProps {
  tokens?: string[]
}

export function RealTimePrices({ tokens = ["SOL", "JTO", "BONK", "RAY"] }: RealTimePricesProps) {
  const [prices, setPrices] = useState<Record<string, PriceData>>({})
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [socket, setSocket] = useState<WebSocket | null>(null)

  const connectWebSocket = useCallback(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8765"
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setIsConnected(true)
      console.log("WebSocket connected")

      // Subscribe to token prices
      tokens.forEach((token) => {
        // Assuming we're getting USDC prices for each token
        const message = {
          type: "subscribe",
          token_pair: {
            input_mint: `${token}_MINT_ADDRESS`, // Replace with actual mint addresses in production
            output_mint: "USDC_MINT_ADDRESS",
          },
        }
        ws.send(JSON.stringify(message))
      })
    }

    ws.onclose = () => {
      setIsConnected(false)
      console.log("WebSocket disconnected")

      // Try to reconnect after a delay
      setTimeout(() => {
        connectWebSocket()
      }, 5000)
    }

    ws.onerror = (error) => {
      console.error("WebSocket error:", error)
      ws.close()
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        if (data.type === "price_update" && data.data) {
          const priceData = data.data
          const tokenSymbol = priceData.symbol || "Unknown"

          setPrices((prev) => ({
            ...prev,
            [tokenSymbol]: {
              symbol: tokenSymbol,
              price: priceData.price,
              price_change_pct: priceData.price_change_pct,
              last_updated: new Date().toISOString(),
            },
          }))
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error)
      }
    }

    setSocket(ws)

    return () => {
      ws.close()
    }
  }, [tokens.join(",")])

  useEffect(() => {
    // Simulate initial loading
    setTimeout(() => {
      setIsLoading(false)
    }, 1500)

    connectWebSocket()

    return () => {
      if (socket) {
        socket.close()
      }
    }
  }, [connectWebSocket])

  // Mock data for initial render
  useEffect(() => {
    if (!isLoading && Object.keys(prices).length === 0) {
      const mockPrices: Record<string, PriceData> = {}
      tokens.forEach((token) => {
        mockPrices[token] = {
          symbol: token,
          price: token === "SOL" ? 100.25 : token === "JTO" ? 2.34 : token === "BONK" ? 0.00000125 : 0.78,
          price_change_pct: token === "SOL" ? 2.5 : token === "JTO" ? -1.2 : token === "BONK" ? 5.7 : -0.3,
          last_updated: new Date().toISOString(),
        }
      })
      setPrices(mockPrices)
    }
  }, [isLoading, tokens])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Real-Time Prices</CardTitle>
        <CardDescription>
          Live token prices from Jupiter
          <Badge variant={isConnected ? "default" : "outline"} className="ml-2">
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {isLoading ? (
            <>
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="flex flex-col space-y-2 p-4 border rounded-lg">
                  <Skeleton className="h-4 w-12 mb-2" />
                  <Skeleton className="h-6 w-24" />
                  <Skeleton className="h-4 w-16" />
                </div>
              ))}
            </>
          ) : (
            <>
              {tokens.map((token) => {
                const priceData = prices[token]
                if (!priceData) return null

                const isPositive = priceData.price_change_pct && priceData.price_change_pct > 0
                const isNegative = priceData.price_change_pct && priceData.price_change_pct < 0

                return (
                  <div key={token} className="flex flex-col p-4 border rounded-lg">
                    <span className="text-sm font-medium text-muted-foreground">{token}</span>
                    <span className="text-2xl font-bold">
                      ${priceData.price < 0.01 ? priceData.price.toFixed(8) : priceData.price.toFixed(2)}
                    </span>
                    <div className="flex items-center mt-1">
                      {isPositive && <ArrowUpIcon className="h-3 w-3 text-green-500 mr-1" />}
                      {isNegative && <ArrowDownIcon className="h-3 w-3 text-red-500 mr-1" />}
                      <span className={`text-sm ${isPositive ? "text-green-500" : isNegative ? "text-red-500" : ""}`}>
                        {priceData.price_change_pct
                          ? `${isPositive ? "+" : ""}${priceData.price_change_pct.toFixed(2)}%`
                          : "0.00%"}
                      </span>
                    </div>
                  </div>
                )
              })}
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
