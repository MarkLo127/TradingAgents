"use client";

import { useState } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  Cell,
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
          <Tabs value={chartType} onValueChange={(v: string) => setChartType(v as "line" | "candlestick")}>
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
              // K線圖：簡化版實現
              <BarChart data={priceData}>
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
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      const isUp = data.Close >= data.Open;
                      return (
                        <div className="bg-background border border-border p-3 rounded-lg shadow-lg">
                          <p className="text-sm font-semibold mb-2">日期: {data.Date}</p>
                          <div className="space-y-1 text-sm">
                            <p className={isUp ? 'text-green-600' : 'text-red-600'}>
                              開: ${formatNumber(data.Open)}
                            </p>
                            <p className={isUp ? 'text-green-600' : 'text-red-600'}>
                              收: ${formatNumber(data.Close)}
                            </p>
                            <p className="text-blue-600">高: ${formatNumber(data.High)}</p>
                            <p className="text-orange-600">低: ${formatNumber(data.Low)}</p>
                            <p className="text-sm text-muted-foreground mt-2">
                              {isUp ? '↑ 上漲' : '↓ 下跌'} ${formatNumber(Math.abs(data.Close - data.Open))}
                            </p>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                {/* 使用 Bar 顯示收盤價，顏色根據漲跌決定 */}
                <Bar 
                  dataKey="Close" 
                  name="收盤價"
                >
                  {priceData.map((entry: any, index: number) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.Close >= entry.Open ? '#22c55e' : '#ef4444'} 
                    />
                  ))}
                </Bar>
              </BarChart>
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
