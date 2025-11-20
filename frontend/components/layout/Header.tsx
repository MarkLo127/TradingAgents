/**
 * Header component
 */
import Link from "next/link";

export function Header() {
  return (
    <header className="border-b bg-gradient-to-r from-blue-600 to-purple-600 text-white">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="text-3xl font-bold">TradingAgents</div>
            <div className="hidden md:block text-sm font-light opacity-90">
              多代理 LLM 金融交易框架
            </div>
          </Link>
          <nav className="flex gap-6">
            <Link
              href="/"
              className="hover:opacity-80 transition-opacity font-medium"
            >
              首頁
            </Link>
            <Link
              href="/analysis"
              className="hover:opacity-80 transition-opacity font-medium"
            >
              分析
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
