"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

// Mock data for recent trades
const mockTrades = [
  {
    id: "1",
    token: "SOL/USDC",
    buyDex: "Jupiter",
    sellDex: "Raydium",
    buyPrice: "$103.45",
    sellPrice: "$104.12",
    profit: "$8.92",
    timestamp: "2023-04-16 14:32:45",
    status: "completed",
  },
  {
    id: "2",
    token: "BONK/USDC",
    buyDex: "Orca",
    sellDex: "Jupiter",
    buyPrice: "$0.00000124",
    sellPrice: "$0.00000129",
    profit: "$6.34",
    timestamp: "2023-04-16 14:28:12",
    status: "completed",
  },
  {
    id: "3",
    token: "RAY/USDC",
    buyDex: "Raydium",
    sellDex: "Meteora",
    buyPrice: "$0.78",
    sellPrice: "$0.79",
    profit: "$4.21",
    timestamp: "2023-04-16 14:25:33",
    status: "completed",
  },
  {
    id: "4",
    token: "JTO/USDC",
    buyDex: "Meteora",
    sellDex: "Orca",
    buyPrice: "$2.34",
    sellPrice: "$2.36",
    profit: "$3.87",
    timestamp: "2023-04-16 14:18:56",
    status: "completed",
  },
  {
    id: "5",
    token: "MNGO/USDC",
    buyDex: "Jupiter",
    sellDex: "Raydium",
    buyPrice: "$0.021",
    sellPrice: "$0.0212",
    profit: "$2.45",
    timestamp: "2023-04-16 14:12:22",
    status: "completed",
  },
]

export default function RecentTradesTable() {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Token Pair</TableHead>
            <TableHead>Buy DEX</TableHead>
            <TableHead>Sell DEX</TableHead>
            <TableHead>Buy Price</TableHead>
            <TableHead>Sell Price</TableHead>
            <TableHead>Profit</TableHead>
            <TableHead>Timestamp</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {mockTrades.map((trade) => (
            <TableRow key={trade.id}>
              <TableCell className="font-medium">{trade.token}</TableCell>
              <TableCell>{trade.buyDex}</TableCell>
              <TableCell>{trade.sellDex}</TableCell>
              <TableCell>{trade.buyPrice}</TableCell>
              <TableCell>{trade.sellPrice}</TableCell>
              <TableCell className="text-green-500">{trade.profit}</TableCell>
              <TableCell>{trade.timestamp}</TableCell>
              <TableCell>
                <Badge
                  variant={
                    trade.status === "completed" ? "success" : trade.status === "failed" ? "destructive" : "default"
                  }
                >
                  {trade.status}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
