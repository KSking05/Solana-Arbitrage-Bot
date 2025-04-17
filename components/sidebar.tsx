"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { BarChart3, Cog, Home, LineChart, Wallet, History, Settings, AlertTriangle } from "lucide-react"

const navItems = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Arbitrage Opportunities", href: "/opportunities", icon: BarChart3 },
  { name: "Trading History", href: "/history", icon: History },
  { name: "Wallet Manager", href: "/wallet", icon: Wallet },
  { name: "Performance", href: "/performance", icon: LineChart },
  { name: "Risk Management", href: "/risk", icon: AlertTriangle },
  { name: "Settings", href: "/settings", icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div
      className={cn(
        "bg-background border-r border-border transition-all duration-300 ease-in-out",
        collapsed ? "w-16" : "w-64",
      )}
    >
      <div className="flex items-center justify-between h-16 px-4 border-b border-border">
        {!collapsed && <span className="text-lg font-semibold">Arbitrage Bot</span>}
        <button onClick={() => setCollapsed(!collapsed)} className="p-2 rounded-md hover:bg-accent">
          <Cog size={20} />
        </button>
      </div>
      <nav className="p-2 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center px-3 py-2 rounded-md transition-colors",
                pathname === item.href ? "bg-primary text-primary-foreground" : "hover:bg-accent",
              )}
            >
              <Icon size={20} />
              {!collapsed && <span className="ml-3">{item.name}</span>}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
