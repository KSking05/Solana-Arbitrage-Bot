"use client"

import { useEffect, useState } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { useTheme } from "next-themes"

interface PerformanceData {
  date: string
  profit: number
  trades: number
  opportunities: number
}

interface PerformanceChartProps {
  data?: PerformanceData[]
}

export default function PerformanceChart({ data = [] }: PerformanceChartProps) {
  const { theme } = useTheme()
  const [mounted, setMounted] = useState(false)
  const [chartData, setChartData] = useState<PerformanceData[]>([])

  useEffect(() => {
    setMounted(true)

    if (data && data.length > 0) {
      setChartData(data)
    } else {
      // Generate mock data if no data is provided
      setChartData(generateMockData())
    }
    // We're using a deep comparison for data, so we need to stringify it
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(data)])

  if (!mounted) {
    return null
  }

  return (
    <div className="w-full h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={theme === "dark" ? "#333" : "#eee"} />
          <XAxis dataKey="date" stroke={theme === "dark" ? "#888" : "#666"} />
          <YAxis yAxisId="left" stroke={theme === "dark" ? "#888" : "#666"} />
          <YAxis yAxisId="right" orientation="right" stroke={theme === "dark" ? "#888" : "#666"} />
          <Tooltip
            contentStyle={{
              backgroundColor: theme === "dark" ? "#1f2937" : "#fff",
              borderColor: theme === "dark" ? "#374151" : "#e5e7eb",
              color: theme === "dark" ? "#fff" : "#000",
            }}
          />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="profit"
            name="Profit ($)"
            stroke="#10b981"
            activeDot={{ r: 8 }}
          />
          <Line yAxisId="right" type="monotone" dataKey="trades" name="Trades Executed" stroke="#3b82f6" />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="opportunities"
            name="Opportunities Detected"
            stroke="#a855f7"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

// Helper function to generate mock data
function generateMockData() {
  const data = []
  const now = new Date()
  for (let i = 29; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    const formattedDate = `${date.getMonth() + 1}/${date.getDate()}`

    // Generate some random but trending upward data
    const baseProfit = 50 + i * 5 + Math.random() * 30
    const trades = Math.floor(10 + i * 0.8 + Math.random() * 5)
    const opportunities = Math.floor(trades * (1.5 + Math.random()))

    data.push({
      date: formattedDate,
      profit: Number.parseFloat(baseProfit.toFixed(2)),
      trades,
      opportunities,
    })
  }
  return data
}
