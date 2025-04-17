"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, BarChart, RefreshCw } from "lucide-react"
import ApiClient from "@/lib/api-client"
import { Skeleton } from "@/components/ui/skeleton"

export default function RiskManagement() {
  const [portfolioRisk, setPortfolioRisk] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const apiClient = new ApiClient()

  const fetchRiskData = async () => {
    try {
      setIsLoading(true)
      const data = await apiClient.getPortfolioRisk()
      setPortfolioRisk(data)
    } catch (error) {
      console.error("Error fetching risk data:", error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchRiskData()
  }, [])

  const handleRefresh = () => {
    fetchRiskData()
  }

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "Low":
        return "bg-green-500"
      case "Medium":
        return "bg-yellow-500"
      case "High":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  if (isLoading || !portfolioRisk) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Risk Management</h1>
          <Button variant="outline" disabled>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Risk Assessment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-4 w-24 mb-2" />
              <Skeleton className="h-8 w-full mb-4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Diversification Analysis</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-8 w-full mb-4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Risk Management</h1>
        <Button variant="outline" onClick={handleRefresh}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xl font-bold">Portfolio Risk Assessment</CardTitle>
            <AlertTriangle className="h-5 w-5 text-yellow-500" />
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Risk Level</span>
              <Badge className={getRiskColor(portfolioRisk.risk_level)}>{portfolioRisk.risk_level}</Badge>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Low Risk</span>
                <span>High Risk</span>
              </div>
              <Progress
                value={
                  portfolioRisk.risk_level === "Low"
                    ? 25
                    : portfolioRisk.risk_level === "Medium"
                      ? 50
                      : portfolioRisk.risk_level === "High"
                        ? 75
                        : 50
                }
                className="h-2"
              />
            </div>
            <div className="pt-4">
              <h3 className="font-medium mb-2">Recommendation</h3>
              <p className="text-sm text-muted-foreground">{portfolioRisk.recommendation}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xl font-bold">Diversification Analysis</CardTitle>
            <BarChart className="h-5 w-5 text-blue-500" />
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Diversification Score</span>
                <span className="font-bold">{portfolioRisk.diversification_score}/10</span>
              </div>
              <Progress value={portfolioRisk.diversification_score * 10} className="h-2" />
            </div>
            <div className="grid grid-cols-2 gap-4 pt-4">
              <div>
                <p className="text-sm text-muted-foreground">Token Count</p>
                <p className="text-xl font-bold">{portfolioRisk.token_count}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Portfolio Value</p>
                <p className="text-xl font-bold">${portfolioRisk.total_value_usd.toFixed(2)}</p>
              </div>
            </div>
            {portfolioRisk.most_concentrated_token && (
              <div className="pt-2">
                <p className="text-sm text-muted-foreground">Highest Concentration</p>
                <div className="flex items-center justify-between">
                  <p className="font-medium">{portfolioRisk.most_concentrated_token}</p>
                  <p className="font-medium">{(portfolioRisk.max_concentration * 100).toFixed(1)}%</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Risk Management Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-medium">Trade Risk Parameters</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Maximum Risk Level</span>
                  <Badge>Medium</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Auto-reject High Risk Trades</span>
                  <Badge variant="outline">Enabled</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Risk Assessment Before Execution</span>
                  <Badge variant="outline">Required</Badge>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-medium">Portfolio Risk Controls</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Maximum Concentration</span>
                  <Badge>40%</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Minimum Tokens</span>
                  <Badge>3</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Daily Loss Limit</span>
                  <Badge variant="destructive">$500</Badge>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
