"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAnalysisContext } from "@/context/AnalysisContext";
import { PriceChart } from "@/components/analysis/PriceChart";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ArrowLeft } from "lucide-react";

const ANALYSTS = [
  { key: "market", label: "市場分析師", reportKey: "market_report" },
  { key: "social", label: "社群媒體分析師", reportKey: "sentiment_report" },
  { key: "news", label: "新聞分析師", reportKey: "news_report" },
  { key: "fundamentals", label: "基本面分析師", reportKey: "fundamentals_report" },
];

export default function AnalysisResultsPage() {
  const router = useRouter();
  const { analysisResult } = useAnalysisContext();
  const [selectedAnalyst, setSelectedAnalyst] = useState("market");

  // 如果沒有結果，重定向到分析頁面
  useEffect(() => {
    if (!analysisResult) {
      router.push("/analysis");
    }
  }, [analysisResult, router]);

  if (!analysisResult) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">沒有分析結果</h1>
          <p className="text-gray-600 mb-4">請先執行分析</p>
          <Button onClick={() => router.push("/analysis")}>
            返回分析頁面
          </Button>
        </div>
      </div>
    );
  }

  const currentAnalyst = ANALYSTS.find(a => a.key === selectedAnalyst);
  const currentReport = analysisResult.reports?.[currentAnalyst?.reportKey || ""];

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
          <div>
            <h1 className="text-4xl font-bold mb-2">
              {analysisResult.ticker} 詳細分析結果
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              分析日期：{analysisResult.analysis_date}
            </p>
          </div>
          <Button 
            variant="outline" 
            onClick={() => router.push("/analysis")}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            返回分析
          </Button>
        </div>

        {/* 分析師選擇 Tabs */}
        <Tabs value={selectedAnalyst} onValueChange={setSelectedAnalyst} className="w-full">
          <TabsList className="grid w-full grid-cols-2 md:grid-cols-4 h-auto gap-2">
            {ANALYSTS.map(analyst => (
              <TabsTrigger 
                key={analyst.key} 
                value={analyst.key}
                className="text-sm md:text-base py-2"
              >
                {analyst.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {ANALYSTS.map(analyst => (
            <TabsContent key={analyst.key} value={analyst.key} className="mt-6">
              <div className="space-y-6">
                {/* 價格圖表 - 每個分析師都有 */}
                {analysisResult.price_data && analysisResult.price_stats && (
                  <PriceChart
                    priceData={analysisResult.price_data}
                    priceStats={analysisResult.price_stats}
                    ticker={analysisResult.ticker}
                  />
                )}

                {/* 分析師報告 */}
                <Card>
                  <CardHeader>
                    <CardTitle>{analyst.label} 報告</CardTitle>
                    <CardDescription>
                      {analyst.key === "market" && "技術分析與市場趨勢評估"}
                      {analyst.key === "social" && "社群情緒與市場氛圍分析"}
                      {analyst.key === "news" && "新聞事件與影響分析"}
                      {analyst.key === "fundamentals" && "財務數據與基本面分析"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {currentReport ? (
                      <div className="prose prose-sm max-w-none dark:prose-invert">
                        <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                          {currentReport}
                        </pre>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-gray-500 dark:text-gray-400">
                          此分析師沒有生成報告
                        </p>
                        <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                          可能此分析師未被選擇或分析過程中未產生報告
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </div>
  );
}
