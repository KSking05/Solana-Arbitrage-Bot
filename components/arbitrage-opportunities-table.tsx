"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useState } from "react"

// Mock data for arbitrage opportunities
const mockOpportunities = [
  {
    id: "1",
    token: "SOL/USDC",
    buyDex: "Jupiter",
    sellDex: "Raydium",
    priceDiff: "0.42%",
    potentialProfit: "$12.45",
    timestamp: "2 sec ago",
    status: "active",
  },
  {
    id: "2",
    token: "BONK/USDC",
    buyDex: "Orca",
    sellDex: "Jupiter",
    priceDiff: "0.38%",
    potentialProfit: "$8.21",
    timestamp: "5 sec ago",
    status: "active",
  },
  {
    id: "3",
    token: "RAY/USDC",
    buyDex: "Raydium",
    sellDex: "Meteora",
    priceDiff: "0.31%",
    potentialProfit: "$5.67",
    timestamp: "12 sec ago",
    status: "active",
  },
  {
    id: "4",
    token: "MNGO/USDC",
    buyDex: "Meteora",
    sellDex: "Orca",
    priceDiff: "0.28%",
    potentialProfit: "$4.92",
    timestamp: "18 sec ago",
    status: "active",
  },
  {
    id: "5",
    token: "JTO/USDC",
    buyDex: "Jupiter",
    sellDex: "Raydium",
    priceDiff: "0.25%",
    potentialProfit: "$3.78",
    timestamp: "25 sec ago",
    status: "expired",
  },
]

export default function ArbitrageOpportunitiesTable() {
  const [opportunities, setOpportunities] = useState(mockOpportunities)

  const executeArbitrage = (id: string) => {
    // In a real application, this would call the backend to execute the trade
    setOpportunities(opportunities.map((opp) => (opp.id === id ? { ...opp, status: "executing" } : opp)))

    // Simulate execution completion after 2 seconds
    setTimeout(() => {
      setOpportunities(opportunities.map((opp) => (opp.id === id ? { ...opp, status: "completed" } : opp)))
    }, 2000)
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
            <TableHead>Detected</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {opportunities.map((opportunity) => (
            <TableRow key={opportunity.id}>
              <TableCell className="font-medium">{opportunity.token}</TableCell>
              <TableCell>{opportunity.buyDex}</TableCell>
              <TableCell>{opportunity.sellDex}</TableCell>
              <TableCell className="text-green-500">{opportunity.priceDiff}</TableCell>
              <TableCell>{opportunity.potentialProfit}</TableCell>
              <TableCell>{opportunity.timestamp}</TableCell>
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
                <Button
                  size="sm"
                  disabled={opportunity.status !== "active"}
                  onClick={() => executeArbitrage(opportunity.id)}
                >
                  {opportunity.status === "executing" ? "Executing..." : "Execute"}
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
