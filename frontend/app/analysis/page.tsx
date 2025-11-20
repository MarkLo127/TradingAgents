/**
 * Analysis page
 */
"use client";

import { useState } from "react";
import { AnalysisForm } from "@/components/analysis/AnalysisForm";
import { TradingDecision } from "@/components/analysis/TradingDecision";
import { AnalystReport } from "@/components/analysis/AnalystReport";
import { PriceChart } from "@/components/analysis/PriceChart";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { useAnalysis } from "@/hooks/useAnalysis";
import type { AnalysisRequest } from "@/lib/types";

export default function AnalysisPage() {
  const { runAnalysis, loading, error, result } = useAnalysis();

  const handleSubmit = async (request: AnalysisRequest) => {
    try {
      await runAnalysis(request);
    } catch (err) {
      // Error is handled by the hook
      console.error("Analysis failed:", err);
    }
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-6xl mx-auto space-y-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">交易分析</h1>
          <p className="text-gray-600 dark:text-gray-400">
            配置並執行全面的多代理交易分析
          </p>
        </div>

        <AnalysisForm onSubmit={handleSubmit} loading={loading} />

        {loading && (
          <LoadingSpinner message="正在執行分析... 這可能需要幾分鐘時間。" />
        )}

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <h3 className="text-red-800 dark:text-red-300 font-semibold mb-2">錯誤</h3>
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {result && !loading && (
          <div className="space-y-8">
            {/* 價格圖表 */}
            {result.price_data && result.price_stats && (
              <PriceChart
                priceData={result.price_data}
                priceStats={result.price_stats}
                ticker={result.ticker}
              />
            )}
            
            {/* 交易決策 */}
            <TradingDecision result={result} />
            
            {/* 分析報告 */}
            {result.reports && <AnalystReport reports={result.reports} />}
          </div>
        )}
      </div>
    </div>
  );
}
