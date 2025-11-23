"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useAnalysisContext } from "@/context/AnalysisContext";
import { PriceChart } from "@/components/analysis/PriceChart";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ChevronLeft } from "lucide-react";

const ANALYSTS = [
  // === 分析師團隊 ===
  { 
    key: "market", 
    label: "市場分析師", 
    reportKey: "market_report",
    description: "技術分析與市場趨勢評估"
  },
  { 
    key: "social", 
    label: "社群媒體分析師", 
    reportKey: "sentiment_report",
    description: "社群情緒與市場氛圍分析"
  },
  { 
    key: "news", 
    label: "新聞分析師", 
    reportKey: "news_report",
    description: "新聞事件與影響分析"
  },
  { 
    key: "fundamentals", 
    label: "基本面分析師", 
    reportKey: "fundamentals_report",
    description: "財務數據與基本面分析"
  },
  
  // === 研究團隊 ===
  { 
    key: "bull", 
    label: "看漲研究員", 
    reportKey: "investment_debate_state.bull_history",
    description: "看漲觀點與投資論據"
  },
  { 
    key: "bear", 
    label: "看跌研究員", 
    reportKey: "investment_debate_state.bear_history",
    description: "看跌觀點與風險警告"
  },
  { 
    key: "research_manager", 
    label: "研究經理", 
    reportKey: "investment_debate_state.judge_decision",
    description: "研究團隊綜合決策"
  },
  
  // === 交易員 ===
  { 
    key: "trader", 
    label: "交易員", 
    reportKey: "trader_investment_plan",
    description: "交易執行計劃與策略"
  },
  
  // === 風險管理團隊 ===
  { 
    key: "risky", 
    label: "激進分析師", 
    reportKey: "risk_debate_state.risky_history",
    description: "高風險高回報策略分析"
  },
  { 
    key: "safe", 
    label: "保守分析師", 
    reportKey: "risk_debate_state.safe_history",
    description: "穩健保守策略分析"
  },
  { 
    key: "neutral", 
    label: "中立分析師", 
    reportKey: "risk_debate_state.neutral_history",
    description: "中立平衡策略分析"
  },
  { 
    key: "risk_manager", 
    label: "風險經理", 
    reportKey: "risk_debate_state.judge_decision",
    description: "風險管理綜合決策"
  },
];

// 獲取嵌套對象的值
const getNestedValue = (obj: any, path: string) => {
  return path.split('.').reduce((current, key) => current?.[key], obj);
};

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
  const currentReport = getNestedValue(analysisResult.reports, currentAnalyst?.reportKey || "");

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
            <ChevronLeft className="h-4 w-4" />
            返回分析
          </Button>
        </div>

        {/* 分析師選擇 Tabs */}
        <Tabs value={selectedAnalyst} onValueChange={setSelectedAnalyst} className="w-full">
          <TabsList className="grid w-full grid-cols-2 md:grid-cols-3 lg:grid-cols-4 h-auto gap-2">
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
                      {analyst.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {currentReport ? (
                      <div className="prose prose-sm max-w-none dark:prose-invert">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {currentReport}
                        </ReactMarkdown>
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
