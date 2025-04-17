import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowUpRight, ArrowDownRight, DollarSign, Activity, BarChart, Clock } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import ArbitrageOpportunitiesTable from "@/components/arbitrage-opportunities-table"
import RecentTradesTable from "@/components/recent-trades-table"
import PerformanceChart from "@/components/performance-chart"

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Profit</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$4,231.89</div>
            <div className="flex items-center text-xs text-green-500">
              <ArrowUpRight className="mr-1 h-4 w-4" />
              <span>+20.1% from last week</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Opportunities</CardTitle>
            <BarChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24</div>
            <div className="flex items-center text-xs text-green-500">
              <ArrowUpRight className="mr-1 h-4 w-4" />
              <span>+12 from last hour</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Trades Executed</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">342</div>
            <div className="flex items-center text-xs text-green-500">
              <ArrowUpRight className="mr-1 h-4 w-4" />
              <span>+18.2% from yesterday</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Response Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">238ms</div>
            <div className="flex items-center text-xs text-red-500">
              <ArrowDownRight className="mr-1 h-4 w-4" />
              <span>+12ms from last hour</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="opportunities" className="space-y-4">
        <TabsList>
          <TabsTrigger value="opportunities">Arbitrage Opportunities</TabsTrigger>
          <TabsTrigger value="recent">Recent Trades</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>
        <TabsContent value="opportunities" className="space-y-4">
          <div className="flex justify-between">
            <h2 className="text-xl font-bold">Current Opportunities</h2>
            <Button>Refresh</Button>
          </div>
          <ArbitrageOpportunitiesTable />
        </TabsContent>
        <TabsContent value="recent" className="space-y-4">
          <div className="flex justify-between">
            <h2 className="text-xl font-bold">Recent Trades</h2>
            <Button>Export</Button>
          </div>
          <RecentTradesTable />
        </TabsContent>
        <TabsContent value="performance" className="space-y-4">
          <div className="flex justify-between">
            <h2 className="text-xl font-bold">Performance Metrics</h2>
            <Button>Last 30 Days</Button>
          </div>
          <Card>
            <CardContent className="pt-6">
              <PerformanceChart />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
