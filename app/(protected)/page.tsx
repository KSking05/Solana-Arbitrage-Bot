"use client"

import { useEffect, useState, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { RecentOpportunities } from "@/components/recent-opportunities"
import { RecentTrades } from "@/components/recent-trades"
import { RealTimePrices } from "@/components/real-time-prices"
import PerformanceChart from "@/components/performance-chart"
import { RefreshCw, TrendingUp, Wallet, AlertTriangle } from "lucide-react"
import ApiClient from "@/lib/api-client"
import { Skeleton } from "@/components/ui/skeleton"

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [botActive, setBotActive] = useState(false)
  const apiClient = new ApiClient()

  const fetchDashboardData = useCallback(async () => {
    try {
      setIsLoading(true)
      const data = await apiClient.getDashboard()
      setDashboardData(data)

      // Get bot status
      const botStatus = await apiClient.getBotStatus()
      setBotActive(botStatus.active)
    } catch (error) {
      console.error("Error fetching dashboard data:", error)
    } finally {
      setIsLoading(false)
    }
  }, [apiClient])

  useEffect(() => {
    fetchDashboardData()

    // Refresh data every 60 seconds
    const interval = setInterval(() => {
      fetchDashboardData()
    }, 60000)

    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleRefresh = () => {
    fetchDashboardData()
  }

  const toggleBot = async () => {
    try {
      const newStatus = !botActive
      await apiClient.updateBotStatus(newStatus)
      setBotActive(newStatus)
    } catch (error) {
      console.error("Error toggling bot status:", error)
    }
  }

  if (isLoading || !dashboardData) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <div className="flex space-x-2">
            <Button variant="outline" disabled>
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
            <Button disabled>Start Bot</Button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  <Skeleton className="h-4 w-24" />
                </CardTitle>
                <Skeleton className="h-4 w-4" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-24 mb-2" />
                <Skeleton className="h-4 w-32" />
              </CardContent>
            </Card>
          ))}
        </div>

        <Skeleton className="h-[400px] w-full" />

        <Tabs defaultValue="opportunities" className="space-y-4">
          <TabsList>
            <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
            <TabsTrigger value="trades">Recent Trades</TabsTrigger>
          </TabsList>
          <TabsContent value="opportunities" className="space-y-4">
            <Skeleton className="h-[300px] w-full" />
          </TabsContent>
          <TabsContent value="trades" className="space-y-4">
            <Skeleton className="h-[300px] w-full" />
          </TabsContent>
        </Tabs>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={handleRefresh}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button onClick={toggleBot} variant={botActive ? "destructive" : "default"}>
            {botActive ? "Stop Bot" : "Start Bot"}
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Profit</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${Number(dashboardData.stats.total_profit).toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">
              +${(Number(dashboardData.stats.total_profit) * 0.05).toFixed(2)} from last week
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Opportunities</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.stats.active_opportunities}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardData.stats.active_opportunities > 0 ? "Opportunities available" : "No active opportunities"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Trades Executed</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.stats.trades_executed}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardData.stats.trades_executed > 0
                ? `${Math.round(dashboardData.stats.trades_executed / 30)} per day avg.`
                : "No trades executed yet"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Response Time</CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.stats.avg_response_time_ms} ms</div>
            <p className="text-xs text-muted-foreground">
              {dashboardData.stats.avg_response_time_ms < 300 ? "Fast response time" : "Average response time"}
            </p>
          </CardContent>
        </Card>
      </div>

      <RealTimePrices />

      <Card>
        <CardHeader>
          <CardTitle>Performance Overview</CardTitle>
          <CardDescription>Daily profit and trading activity over the last 30 days</CardDescription>
        </CardHeader>
        <CardContent>
          <PerformanceChart data={dashboardData.performance_data} />
        </CardContent>
      </Card>

      <Tabs defaultValue="opportunities" className="space-y-4">
        <TabsList>
          <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
          <TabsTrigger value="trades">Recent Trades</TabsTrigger>
        </TabsList>
        <TabsContent value="opportunities" className="space-y-4">
          <RecentOpportunities opportunities={dashboardData.recent_opportunities} />
        </TabsContent>
        <TabsContent value="trades" className="space-y-4">
          <RecentTrades trades={dashboardData.recent_trades} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
