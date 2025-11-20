"use client";

import { useState } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Area,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { PriceData, PriceStats } from "@/lib/types";

interface PriceChartProps {
  priceData: PriceData[];
  priceStats: PriceStats;
  ticker: string;
}

export function PriceChart({ priceData, priceStats, ticker }: PriceChartProps) {
  const [chartType, setChartType] = useState<"line" | "candlestick">("line");

  // 格式化數字
  const formatNumber = (num: number) => {
    return num.toLocaleString('zh-TW', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  // 格式化日期（只顯示月-日）
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="text-2xl">{ticker} 價格走勢</CardTitle>
          <Tabs value={chartType} onValueChange={(v) => setChartType(v as "line" | "candlestick")}>
            <TabsList>
              <TabsTrigger value="line">折線圖</TabsTrigger>
              <TabsTrigger value="candlestick">K線圖</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {/* 統計資訊 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div className="bg-muted p-4 rounded-lg">
            <p className="text-sm text-muted-foreground">增長率</p>
            <p className={`text-2xl font-bold ${priceStats.growth_rate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {priceStats.growth_rate >= 0 ? '+' : ''}{priceStats.growth_rate}%
            </p>
          </div>
          <div className="bg-muted p-4 rounded-lg">
            <p className="text-sm text-muted-foreground">時長</p>
            <p className="text-2xl font-bold">{priceStats.duration_days} 天</p>
          </div>
          <div className="bg-muted p-4 rounded-lg">
            <p className="text-sm text-muted-foreground">起始價格</p>
            <p className="text-lg font-semibold">${formatNumber(priceStats.start_price)}</p>
            <p className="text-xs text-muted-foreground">{priceStats.start_date}</p>
          </div>
          <div className="bg-muted p-4 rounded-lg">
            <p className="text-sm text-muted-foreground">結束價格</p>
            <p className="text-lg font-semibold">${formatNumber(priceStats.end_price)}</p>
            <p className="text-xs text-muted-foreground">{priceStats.end_date}</p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* 價格圖表 */}
        <div>
          <h3 className="text-lg font-semibold mb-4">價格走勢</h3>
          <ResponsiveContainer width="100%" height={400}>
            {chartType === "line" ? (
              <LineChart data={priceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="Date" 
                  tickFormatter={formatDate}
                  minTickGap={30}
                />
                <YAxis 
                  domain={['auto', 'auto']}
                  tickFormatter={(value) => `$${value.toFixed(0)}`}
                />
                <Tooltip 
                  formatter={(value: number) => [`$${formatNumber(value)}`, '收盤價']}
                  labelFormatter={(label) => `日期: ${label}`}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="Close" 
                  stroke="#2563eb" 
                  strokeWidth={2}
                  name="收盤價" 
                  dot={false}
                />
              </LineChart>
            ) : (
              <ComposedChart data={priceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="Date" 
                  tickFormatter={formatDate}
                  minTickGap={30}
                />
                <YAxis 
                  domain={['auto', 'auto']}
                  tickFormatter={(value) => `$${value.toFixed(0)}`}
                />
                <Tooltip 
                  formatter={(value: number, name: string) => [`$${formatNumber(value)}`, name]}
                  labelFormatter={(label) => `日期: ${label}`}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="High" 
                  stroke="#86efac" 
                  fill="#86efac"
                  fillOpacity={0.3}
                  name="最高價"
                />
                <Area 
                  type="monotone" 
                  dataKey="Low" 
                  stroke="#fca5a5" 
                  fill="#fca5a5"
                  fillOpacity={0.3}
                  name="最低價"
                />
                <Line 
                  type="monotone" 
                  dataKey="Open" 
                  stroke="#f59e0b" 
                  strokeWidth={2}
                  name="開盤價"
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="Close" 
                  stroke="#2563eb" 
                  strokeWidth={2}
                  name="收盤價"
                  dot={false}
                />
              </ComposedChart>
            )}
          </ResponsiveContainer>
        </div>

        {/* 交易量圖表 */}
        <div>
          <h3 className="text-lg font-semibold mb-4">交易量</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={priceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="Date" 
                tickFormatter={formatDate}
                minTickGap={30}
              />
              <YAxis 
                tickFormatter={(value) => {
                  if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
                  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
                  return value.toString();
                }}
              />
              <Tooltip 
                formatter={(value: number) => [value.toLocaleString(), '交易量']}
                labelFormatter={(label) => `日期: ${label}`}
              />
              <Bar dataKey="Volume" fill="#10b981" name="交易量" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
