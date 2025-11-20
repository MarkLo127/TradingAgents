/**
 * Analyst reports display component
 */
"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { Reports } from "@/lib/types";

interface AnalystReportProps {
  reports: Reports;
}

export function AnalystReport({ reports }: AnalystReportProps) {
  const hasAnalystReports =
    reports.market_report ||
    reports.sentiment_report ||
    reports.news_report ||
    reports.fundamentals_report;

  const hasResearchReports =
    reports.investment_debate_state?.bull_history ||
    reports.investment_debate_state?.bear_history ||
    reports.investment_debate_state?.judge_decision;

  const hasRiskReports =
    reports.risk_debate_state?.risky_history ||
    reports.risk_debate_state?.safe_history ||
    reports.risk_debate_state?.neutral_history;

  if (!hasAnalystReports && !hasResearchReports && !hasRiskReports) {
    return null;
  }

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle>分析報告</CardTitle>
        <CardDescription>來自所有代理團隊的詳細報告</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="analysts" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="analysts">分析師</TabsTrigger>
            <TabsTrigger value="research">研究</TabsTrigger>
            <TabsTrigger value="trader">交易員</TabsTrigger>
            <TabsTrigger value="risk">風險</TabsTrigger>
          </TabsList>

          <TabsContent value="analysts" className="space-y-4">
            {reports.market_report && (
              <ReportSection title="市場分析" content={reports.market_report} />
            )}
            {reports.sentiment_report && (
              <ReportSection title="情緒分析" content={reports.sentiment_report} />
            )}
            {reports.news_report && (
              <ReportSection title="新聞分析" content={reports.news_report} />
            )}
            {reports.fundamentals_report && (
              <ReportSection title="基本面分析" content={reports.fundamentals_report} />
            )}
          </TabsContent>

          <TabsContent value="research" className="space-y-4">
            {reports.investment_debate_state?.bull_history && (
              <ReportSection
                title="看漲研究員"
                content={reports.investment_debate_state.bull_history}
              />
            )}
            {reports.investment_debate_state?.bear_history && (
              <ReportSection
                title="看跌研究員"
                content={reports.investment_debate_state.bear_history}
              />
            )}
            {reports.investment_debate_state?.judge_decision && (
              <ReportSection
                title="研究經理決策"
                content={reports.investment_debate_state.judge_decision}
              />
            )}
          </TabsContent>

          <TabsContent value="trader" className="space-y-4">
            {reports.trader_investment_plan && (
              <ReportSection title="交易員計劃" content={reports.trader_investment_plan} />
            )}
          </TabsContent>

          <TabsContent value="risk" className="space-y-4">
            {reports.risk_debate_state?.risky_history && (
              <ReportSection
                title="激進分析師"
                content={reports.risk_debate_state.risky_history}
              />
            )}
            {reports.risk_debate_state?.safe_history && (
              <ReportSection
                title="保守分析師"
                content={reports.risk_debate_state.safe_history}
              />
            )}
            {reports.risk_debate_state?.neutral_history && (
              <ReportSection
                title="中立分析師"
                content={reports.risk_debate_state.neutral_history}
              />
            )}
            {reports.risk_debate_state?.judge_decision && (
              <ReportSection
                title="投資組合經理決策"
                content={reports.risk_debate_state.judge_decision}
              />
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

function ReportSection({ title, content }: { title: string; content: string }) {
  return (
    <div className="border rounded-lg p-4">
      <h3 className="font-semibold text-lg mb-2">{title}</h3>
      <div className="prose prose-sm dark:prose-invert max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
