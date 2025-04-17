"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Slider } from "@/components/ui/slider"
import { toast } from "@/components/ui/use-toast"

export default function Settings() {
  const [isLoading, setIsLoading] = useState(false)

  const saveSettings = () => {
    setIsLoading(true)
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false)
      toast({
        title: "Settings saved",
        description: "Your bot settings have been updated successfully.",
      })
    }, 1500)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Bot Settings</h1>
        <Button onClick={saveSettings} disabled={isLoading}>
          {isLoading ? "Saving..." : "Save Settings"}
        </Button>
      </div>

      <Tabs defaultValue="general" className="space-y-4">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="trading">Trading Parameters</TabsTrigger>
          <TabsTrigger value="dexes">DEX Configuration</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>General Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="bot-name">Bot Name</Label>
                  <Input id="bot-name" defaultValue="Solana Arbitrage Bot" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="refresh-rate">Price Refresh Rate (ms)</Label>
                  <Input id="refresh-rate" type="number" defaultValue="500" min="100" />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="auto-start">Auto-start on boot</Label>
                  <Switch id="auto-start" defaultChecked />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="debug-mode">Debug Mode</Label>
                  <Switch id="debug-mode" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trading" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Trading Parameters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="min-profit">Minimum Profit Threshold (%)</Label>
                  <Input id="min-profit" type="number" defaultValue="0.25" step="0.01" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="max-slippage">Maximum Slippage (%)</Label>
                  <Input id="max-slippage" type="number" defaultValue="0.5" step="0.1" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="min-trade">Minimum Trade Size (USDC)</Label>
                  <Input id="min-trade" type="number" defaultValue="10" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="max-trade">Maximum Trade Size (USDC)</Label>
                  <Input id="max-trade" type="number" defaultValue="1000" />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Risk Level</Label>
                <Slider defaultValue={[5]} max={10} step={1} className="w-full" />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Conservative</span>
                  <span>Balanced</span>
                  <span>Aggressive</span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="auto-execute">Auto-execute profitable trades</Label>
                  <Switch id="auto-execute" defaultChecked />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dexes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>DEX Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <img
                      src="/placeholder.svg?height=24&width=24&query=Jupiter"
                      alt="Jupiter"
                      className="w-6 h-6 rounded-full"
                    />
                    <Label>Jupiter</Label>
                  </div>
                  <Switch defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <img
                      src="/placeholder.svg?height=24&width=24&query=Raydium"
                      alt="Raydium"
                      className="w-6 h-6 rounded-full"
                    />
                    <Label>Raydium</Label>
                  </div>
                  <Switch defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <img
                      src="/placeholder.svg?height=24&width=24&query=Orca"
                      alt="Orca"
                      className="w-6 h-6 rounded-full"
                    />
                    <Label>Orca</Label>
                  </div>
                  <Switch defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <img
                      src="/placeholder.svg?height=24&width=24&query=Meteora"
                      alt="Meteora"
                      className="w-6 h-6 rounded-full"
                    />
                    <Label>Meteora</Label>
                  </div>
                  <Switch defaultChecked />
                </div>
              </div>

              <div className="pt-4">
                <Label>API Configuration</Label>
                <div className="grid grid-cols-2 gap-4 mt-2">
                  <div className="space-y-2">
                    <Label htmlFor="jupiter-api">Jupiter API Key</Label>
                    <Input id="jupiter-api" type="password" value="••••••••••••••••" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="rpc-url">RPC URL</Label>
                    <Input id="rpc-url" defaultValue="https://api.mainnet-beta.solana.com" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Notification Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="email-notifications">Email Notifications</Label>
                  <Switch id="email-notifications" defaultChecked />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email-address">Email Address</Label>
                <Input id="email-address" type="email" defaultValue="user@example.com" />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="telegram-notifications">Telegram Notifications</Label>
                  <Switch id="telegram-notifications" />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="telegram-bot-token">Telegram Bot Token</Label>
                <Input id="telegram-bot-token" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="telegram-chat-id">Telegram Chat ID</Label>
                <Input id="telegram-chat-id" />
              </div>

              <div className="space-y-2">
                <Label>Notification Events</Label>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  <div className="flex items-center space-x-2">
                    <Switch id="notify-trade" defaultChecked />
                    <Label htmlFor="notify-trade">Successful Trades</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch id="notify-error" defaultChecked />
                    <Label htmlFor="notify-error">Errors</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch id="notify-opportunity" />
                    <Label htmlFor="notify-opportunity">New Opportunities</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch id="notify-balance" />
                    <Label htmlFor="notify-balance">Balance Updates</Label>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="execution-strategy">Execution Strategy</Label>
                <Select defaultValue="parallel">
                  <SelectTrigger id="execution-strategy">
                    <SelectValue placeholder="Select strategy" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sequential">Sequential</SelectItem>
                    <SelectItem value="parallel">Parallel</SelectItem>
                    <SelectItem value="optimized">Optimized</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="gas-adjustment">Gas Price Adjustment (%)</Label>
                <Input id="gas-adjustment" type="number" defaultValue="10" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="timeout">Transaction Timeout (ms)</Label>
                <Input id="timeout" type="number" defaultValue="30000" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="retry-attempts">Retry Attempts</Label>
                <Input id="retry-attempts" type="number" defaultValue="3" />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="simulation">Simulate Before Execution</Label>
                  <Switch id="simulation" defaultChecked />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="priority-fee">Use Priority Fee</Label>
                  <Switch id="priority-fee" defaultChecked />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
