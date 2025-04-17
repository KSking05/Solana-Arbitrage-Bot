"use client"

import { useState } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { AlertTriangle } from "lucide-react"
import ApiClient from "@/lib/api-client"
import { toast } from "@/components/ui/use-toast"

interface Opportunity {
  id: string
  token: string
  buyDex: string
  sellDex: string
  priceDiff: string
  potentialProfit: string
  timestamp: string
  status: string
}

interface RecentOpportunitiesProps {
  opportunities: Opportunity[]
}

export function RecentOpportunities({ opportunities = [] }: RecentOpportunitiesProps) {
  const [executingId, setExecutingId] = useState<string | null>(null)
  const [riskData, setRiskData] = useState<any>(null)
  const [isLoadingRisk, setIsLoadingRisk] = useState(false)
  const apiClient = new ApiClient()

  const executeArbitrage = async (id: string) => {
    try {
      setExecutingId(id)
      await apiClient.executeOpportunity(id)
      toast({
        title: "Arbitrage executed",
        description: "The arbitrage opportunity is being executed.",
      })
    } catch (error) {
      console.error("Error executing arbitrage:", error)
    } finally {
      setExecutingId(null)
    }
  }

  const checkRisk = async (id: string) => {
    try {
      setIsLoadingRisk(true)
      const data = await apiClient.getTradeRisk(Number.parseInt(id))
      setRiskData(data)
    } catch (error) {
      console.error("Error checking risk:", error)
    } finally {
      setIsLoadingRisk(false)
    }
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Token Pair</TableHead>
            <TableHead>Buy DEX</TableHead>
            <TableHead>Sell DEX</TableHead>
            <TableHead>Price Diff</TableHead>
            <TableHead>Potential Profit</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {opportunities.length === 0 ? (
            <TableRow>
              <TableCell colSpan={7} className="text-center py-4">
                No active opportunities found
              </TableCell>
            </TableRow>
          ) : (
            opportunities.map((opportunity) => (
              <TableRow key={opportunity.id}>
                <TableCell className="font-medium">{opportunity.token}</TableCell>
                <TableCell>{opportunity.buyDex}</TableCell>
                <TableCell>{opportunity.sellDex}</TableCell>
                <TableCell className="text-green-500">{opportunity.priceDiff}</TableCell>
                <TableCell>{opportunity.potentialProfit}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      opportunity.status === "active"
                        ? "success"
                        : opportunity.status === "executing"
                          ? "default"
                          : opportunity.status === "completed"
                            ? "secondary"
                            : "outline"
                    }
                  >
                    {opportunity.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex space-x-2">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm" onClick={() => checkRisk(opportunity.id)}>
                          Risk
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Risk Assessment</DialogTitle>
                          <DialogDescription>
                            Analysis of the risk factors for this arbitrage opportunity.
                          </DialogDescription>
                        </DialogHeader>
                        {isLoadingRisk ? (
                          <div className="flex justify-center py-4">Loading risk data...</div>
                        ) : riskData ? (
                          <div className="space-y-4">
                            <div className="flex items-center justify-between">
                              <span>Risk Score:</span>
                              <Badge
                                variant={
                                  riskData.risk_score <= 3
                                    ? "success"
                                    : riskData.risk_score <= 6
                                      ? "default"
                                      : "destructive"
                                }
                              >
                                {riskData.risk_score}/10
                              </Badge>
                            </div>
                            <div className="flex items-start gap-2">
                              <AlertTriangle
                                className={
                                  riskData.risk_score <= 3
                                    ? "text-green-500"
                                    : riskData.risk_score <= 6
                                      ? "text-yellow-500"
                                      : "text-red-500"
                                }
                              />
                              <p>{riskData.recommendation}</p>
                            </div>
                            <div className="text-sm text-muted-foreground">
                              <p>Price difference: {riskData.factors?.price_difference.toFixed(2)}%</p>
                              <p>Minimum threshold: {riskData.factors?.min_threshold.toFixed(2)}%</p>
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-4">No risk data available</div>
                        )}
                        <DialogFooter>
                          <Button
                            onClick={() => executeArbitrage(opportunity.id)}
                            disabled={
                              opportunity.status !== "active" ||
                              executingId === opportunity.id ||
                              (riskData && !riskData.can_execute)
                            }
                          >
                            {executingId === opportunity.id ? "Executing..." : "Execute Trade"}
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                    <Button
                      size="sm"
                      disabled={opportunity.status !== "active" || executingId === opportunity.id}
                      onClick={() => executeArbitrage(opportunity.id)}
                    >
                      {executingId === opportunity.id ? "Executing..." : "Execute"}
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}
