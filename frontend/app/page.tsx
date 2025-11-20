import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          TradingAgents
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
          多代理 LLM 金融交易框架
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/analysis">
            <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              開始分析
            </Button>
          </Link>
          <a
            href="https://github.com/TauricResearch/TradingAgents"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button size="lg" variant="outline">
              前往 GitHub
            </Button>
          </a>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
        <FeatureCard
          title="分析師團隊"
          description="由 AI 代理驅動的市場、情緒、新聞與基本面分析"
          icon="📊"
        />
        <FeatureCard
          title="研究團隊"
          description="看漲與看跌研究員進行辯論以找出最佳策略"
          icon="🔍"
        />
        <FeatureCard
          title="交易代理"
          description="整合見解並做出明智的交易決策"
          icon="💼"
        />
        <FeatureCard
          title="風險管理"
          description="評估投資組合風險並調整策略"
          icon="🛡️"
        />
      </div>

      {/* Workflow Section */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle>運作方式</CardTitle>
          <CardDescription>
            TradingAgents 模擬真實交易公司，配備專業化的 LLM 代理
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <WorkflowStep
              number={1}
              title="分析師團隊"
              description="多位分析師評估市場狀況、情緒、新聞和基本面"
            />
            <WorkflowStep
              number={2}
              title="研究團隊"
              description="看漲和看跌研究員進行結構化辯論"
            />
            <WorkflowStep
              number={3}
              title="交易員"
              description="審查所有報告並確定交易行動"
            />
            <WorkflowStep
              number={4}
              title="風險管理"
              description="評估風險因素並提供建議"
            />
            <WorkflowStep
              number={5}
              title="投資組合經理"
              description="做出最終決定以批准或拒絕交易"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function FeatureCard({ title, description, icon }: { title: string; description: string; icon: string }) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="text-4xl mb-2">{icon}</div>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
      </CardContent>
    </Card>
  );
}

function WorkflowStep({ number, title, description }: { number: number; title: string; description: string }) {
  return (
    <div className="flex gap-4 items-start">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center justify-center font-bold">
        {number}
      </div>
      <div>
        <h4 className="font-semibold mb-1">{title}</h4>
        <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
      </div>
    </div>
  );
}
