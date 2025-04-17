"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { MoonIcon, SunIcon } from "lucide-react"
import { useTheme } from "next-themes"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

export default function Header() {
  const { setTheme, theme } = useTheme()
  const [botStatus, setBotStatus] = useState<"active" | "inactive">("inactive")
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return (
    <header className="border-b border-border h-16 px-4 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <h1 className="text-xl font-bold">Solana Arbitrage Bot</h1>
        <Badge
          variant={botStatus === "active" ? "success" : "destructive"}
          className={botStatus === "active" ? "bg-green-500 hover:bg-green-600" : "bg-red-500 hover:bg-red-600"}
        >
          {botStatus === "active" ? "Active" : "Inactive"}
        </Badge>
      </div>

      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2">
          <Switch
            id="bot-status"
            checked={botStatus === "active"}
            onCheckedChange={(checked) => setBotStatus(checked ? "active" : "inactive")}
          />
          <Label htmlFor="bot-status">Trading Bot</Label>
        </div>

        <Button variant="ghost" size="icon" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
          {theme === "dark" ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
        </Button>
      </div>
    </header>
  )
}
