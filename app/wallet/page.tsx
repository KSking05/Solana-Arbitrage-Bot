"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Wallet, Plus, RefreshCw, Download, Upload } from "lucide-react"

// Mock wallet data
const mockWalletData = {
  address: "7xKXtg2CdnPTQj8k2GyKHzQPGajXL8KRrhMRLpTbX4Py",
  balance: "45.32 SOL",
  usdValue: "$4,678.96",
  tokens: [
    {
      symbol: "SOL",
      name: "Solana",
      balance: "45.32",
      usdValue: "$4,678.96",
      icon: "/abstract-sol.png",
    },
    {
      symbol: "USDC",
      name: "USD Coin",
      balance: "1,245.67",
      usdValue: "$1,245.67",
      icon: "/digital-usdc-flow.png",
    },
    {
      symbol: "BONK",
      name: "Bonk",
      balance: "12,345,678",
      usdValue: "$123.45",
      icon: "/doge-baseball.png",
    },
    {
      symbol: "RAY",
      name: "Raydium",
      balance: "156.78",
      usdValue: "$78.39",
      icon: "/sunbeam-through-leaves.png",
    },
    {
      symbol: "JTO",
      name: "Jito",
      balance: "34.56",
      usdValue: "$103.68",
      icon: "/abstract-geometric-jto.png",
    },
  ],
}

export default function WalletManager() {
  const [walletData, setWalletData] = useState(mockWalletData)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const refreshWallet = () => {
    setIsRefreshing(true)
    // Simulate API call
    setTimeout(() => {
      setIsRefreshing(false)
    }, 1500)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Wallet Manager</h1>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={refreshWallet} disabled={isRefreshing}>
            <RefreshCw className="mr-2 h-4 w-4" />
            {isRefreshing ? "Refreshing..." : "Refresh"}
          </Button>
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Connect Wallet
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Connect Wallet</DialogTitle>
                <DialogDescription>Connect your Solana wallet to the arbitrage bot.</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="wallet-address">Wallet Address</Label>
                  <Input id="wallet-address" placeholder="Enter your Solana wallet address" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="private-key">Private Key (Optional)</Label>
                  <Input id="private-key" type="password" placeholder="For automated trading (stored securely)" />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit">Connect</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Wallet className="mr-2 h-5 w-5" />
              Wallet Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Wallet Address</p>
                <p className="text-sm font-mono break-all">{walletData.address}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">SOL Balance</p>
                  <p className="text-2xl font-bold">{walletData.balance}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Value</p>
                  <p className="text-2xl font-bold">{walletData.usdValue}</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  <Download className="mr-2 h-4 w-4" />
                  Deposit
                </Button>
                <Button variant="outline" size="sm">
                  <Upload className="mr-2 h-4 w-4" />
                  Withdraw
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Trading Allocation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Maximum Trade Size</p>
                <div className="flex items-center space-x-2">
                  <Input type="number" defaultValue="100" className="w-24" />
                  <span>USDC</span>
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Maximum Daily Trading Volume</p>
                <div className="flex items-center space-x-2">
                  <Input type="number" defaultValue="1000" className="w-24" />
                  <span>USDC</span>
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Risk Level</p>
                <div className="flex items-center space-x-2">
                  <Input type="range" min="1" max="10" defaultValue="5" className="w-full" />
                  <span>5/10</span>
                </div>
              </div>
              <Button className="w-full">Save Settings</Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Token Balances</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Token</TableHead>
                <TableHead>Name</TableHead>
                <TableHead className="text-right">Balance</TableHead>
                <TableHead className="text-right">USD Value</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {walletData.tokens.map((token) => (
                <TableRow key={token.symbol}>
                  <TableCell className="font-medium">
                    <div className="flex items-center">
                      <img
                        src={token.icon || "/placeholder.svg"}
                        alt={token.symbol}
                        className="w-6 h-6 mr-2 rounded-full"
                      />
                      {token.symbol}
                    </div>
                  </TableCell>
                  <TableCell>{token.name}</TableCell>
                  <TableCell className="text-right">{token.balance}</TableCell>
                  <TableCell className="text-right">{token.usdValue}</TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm">
                        Trade
                      </Button>
                      <Button variant="outline" size="sm">
                        Transfer
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
