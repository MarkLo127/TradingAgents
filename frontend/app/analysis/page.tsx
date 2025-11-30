/**
 * Analysis page
 */
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AnalysisForm } from "@/components/analysis/AnalysisForm";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { useAnalysis } from "@/hooks/useAnalysis";
import { useAnalysisContext } from "@/context/AnalysisContext";
import type { AnalysisRequest } from "@/lib/types";

export default function AnalysisPage() {
  const router = useRouter();
  const { setAnalysisResult, setTaskId } = useAnalysisContext();
  const { runAnalysis, loading, error, result, taskId } = useAnalysis();

  // 當分析完成時自動跳轉到結果頁面
  useEffect(() => {
    if (result && !loading && !error) {
      setAnalysisResult(result);
      if (taskId) {
        setTaskId(taskId);
      }
      router.push("/analysis/results");
    }
  }, [result, loading, error, router, setAnalysisResult, taskId, setTaskId]);

  const handleSubmit = async (data: AnalysisRequest) => {
    try {
      await runAnalysis(data);
    } catch (err) {
      // Error is handled by the hook
      console.error("Analysis failed:", err);
    }
  };

  const handleViewResults = () => {
    if (result) {
      setAnalysisResult(result);
      router.push("/analysis/results");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-purple-900/20 dark:to-blue-900/20">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto space-y-8">
        {/* 標題區域 - 置中對齊 */}
        <div className="text-center relative">
          <div className="absolute inset-0 gradient-bg-radial opacity-40 -z-10" />
          <h1 className="text-4xl font-bold mb-2 gradient-text-primary">交易分析</h1>
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
        </div>
      </div>
    </div>
  );
}
