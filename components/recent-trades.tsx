"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { ExternalLink } from "lucide-react"

interface Trade {
  id: string
  token: string
  buyDex: string
  sellDex: string
  buyPrice: string
  sellPrice: string
  profit: string
  timestamp: string
  status: string
  txHashBuy?: string
  txHashSell?: string
}

interface RecentTradesProps {
  trades: Trade[]
}

export function RecentTrades({ trades = [] }: RecentTradesProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(date)
  }

  const openExplorer = (txHash: string) => {
    window.open(`https://explorer.solana.com/tx/${txHash}`, "_blank")
  }

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
            <TableHead>Time</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Details</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {trades.length === 0 ? (
            <TableRow>
              <TableCell colSpan={9} className="text-center py-4">
                No trades found
              </TableCell>
            </TableRow>
          ) : (
            trades.map((trade) => (
              <TableRow key={trade.id}>
                <TableCell className="font-medium">{trade.token}</TableCell>
                <TableCell>{trade.buyDex}</TableCell>
                <TableCell>{trade.sellDex}</TableCell>
                <TableCell>{trade.buyPrice}</TableCell>
                <TableCell>{trade.sellPrice}</TableCell>
                <TableCell className="text-green-500">{trade.profit}</TableCell>
                <TableCell>
                  {typeof trade.timestamp === "string" ? formatDate(trade.timestamp) : trade.timestamp}
                </TableCell>
                <TableCell>
                  <Badge
                    variant={
                      trade.status === "completed" ? "success" : trade.status === "failed" ? "destructive" : "default"
                    }
                  >
                    {trade.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="outline" size="sm">
                        View
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Trade Details</DialogTitle>
                        <DialogDescription>Complete information about this arbitrage trade.</DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-medium text-muted-foreground">Token</p>
                            <p>{trade.token}</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-muted-foreground">Status</p>
                            <Badge
                              variant={
                                trade.status === "completed"
                                  ? "success"
                                  : trade.status === "failed"
                                    ? "destructive"
                                    : "default"
                              }
                            >
                              {trade.status}
                            </Badge>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-medium text-muted-foreground">Buy DEX</p>
                            <p>{trade.buyDex}</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-muted-foreground">Sell DEX</p>
                            <p>{trade.sellDex}</p>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-medium text-muted-foreground">Buy Price</p>
                            <p>{trade.buyPrice}</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-muted-foreground">Sell Price</p>
                            <p>{trade.sellPrice}</p>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-medium text-muted-foreground">Profit</p>
                            <p className="text-green-500 font-medium">{trade.profit}</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-muted-foreground">Time</p>
                            <p>{typeof trade.timestamp === "string" ? formatDate(trade.timestamp) : trade.timestamp}</p>
                          </div>
                        </div>
                        {(trade.txHashBuy || trade.txHashSell) && (
                          <div className="pt-2">
                            <p className="text-sm font-medium text-muted-foreground mb-2">Transaction Hashes</p>
                            {trade.txHashBuy && (
                              <div className="flex items-center justify-between mb-2">
                                <p className="text-xs font-mono truncate max-w-[300px]">{trade.txHashBuy}</p>
                                <Button variant="outline" size="sm" onClick={() => openExplorer(trade.txHashBuy!)}>
                                  <ExternalLink className="h-4 w-4" />
                                </Button>
                              </div>
                            )}
                            {trade.txHashSell && (
                              <div className="flex items-center justify-between">
                                <p className="text-xs font-mono truncate max-w-[300px]">{trade.txHashSell}</p>
                                <Button variant="outline" size="sm" onClick={() => openExplorer(trade.txHashSell!)}>
                                  <ExternalLink className="h-4 w-4" />
                                </Button>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </DialogContent>
                  </Dialog>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}
