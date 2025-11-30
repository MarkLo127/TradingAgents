/**
 * Analysis form component
 */
"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { format } from "date-fns";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { AnalysisRequest } from "@/lib/types";

const formSchema = z.object({
  ticker: z.string().min(1, "股票代碼為必填").max(10),
  analysis_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, "日期格式必須為 YYYY-MM-DD"),
  analysts: z.array(z.string()).min(1, "請至少選擇一位分析師"),
  research_depth: z.number().int().min(1).max(5),
  quick_think_llm: z.string().min(1, "請選擇快速思維模型"),
  deep_think_llm: z.string().min(1, "請選擇深層思維模型"),

  // API Configuration
  quick_think_base_url: z
    .string()
    .url("請輸入有效的 URL")
    .optional()
    .or(z.literal("")),
  deep_think_base_url: z
    .string()
    .url("請輸入有效的 URL")
    .optional()
    .or(z.literal("")),
  quick_think_api_key: z.string().optional().or(z.literal("")),
  deep_think_api_key: z.string().optional().or(z.literal("")),
  embedding_base_url: z
    .string()
    .url("請輸入有效的 URL")
    .optional()
    .or(z.literal("")),
  embedding_api_key: z.string().optional().or(z.literal("")),
  alpha_vantage_api_key: z.string().min(1, "請輸入 Alpha Vantage API Key"),
});

interface AnalysisFormProps {
  onSubmit: (data: AnalysisRequest) => void;
  loading?: boolean;
}

const ANALYSTS = [
  { value: "market", label: "市場分析師" },
  { value: "social", label: "社群媒體分析師" },
  { value: "news", label: "新聞分析師" },
  { value: "fundamentals", label: "基本面分析師" },
];

export function AnalysisForm({ onSubmit, loading = false }: AnalysisFormProps) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      ticker: "NVDA",
      analysis_date: format(new Date(), "yyyy-MM-dd"),
      analysts: ["market", "social", "news", "fundamentals"], // 預設全選
      research_depth: 3, // 預設中等層級
      quick_think_llm: "gpt-5-mini-2025-08-07",
      deep_think_llm: "gpt-5-mini-2025-08-07",
      quick_think_base_url: "https://api.openai.com/v1",
      deep_think_base_url: "https://api.openai.com/v1",
      quick_think_api_key: "",
      deep_think_api_key: "",
      embedding_base_url: "https://api.openai.com/v1",
      embedding_api_key: "",
      alpha_vantage_api_key: "",
    },
  });

  // 全選/取消全選
  const toggleSelectAll = () => {
    const currentAnalysts = form.getValues("analysts");
    if (currentAnalysts.length === ANALYSTS.length) {
      form.setValue("analysts", []);
    } else {
      form.setValue(
        "analysts",
        ANALYSTS.map((a) => a.value)
      );
    }
  };

  function handleSubmit(values: z.infer<typeof formSchema>) {
    const request: AnalysisRequest = {
      ...values,
    };
    onSubmit(request);
  }

  return (
    <Card className="shadow-lg">
      <CardContent className="pt-6">
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleSubmit)}
            className="space-y-6"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 分析師選擇區塊 - 全寬 */}
              <div className="md:col-span-2 border-b pb-6">
                <div className="flex justify-between items-center mb-4">
                  <FormLabel className="text-base font-semibold">
                    分析師團隊
                  </FormLabel>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={toggleSelectAll}
                  >
                    {form.watch("analysts").length === ANALYSTS.length
                      ? "取消全選"
                      : "全選"}
                  </Button>
                </div>
                <FormField
                  control={form.control}
                  name="analysts"
                  render={() => (
                    <FormItem>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {ANALYSTS.map((analyst) => (
                          <FormField
                            key={analyst.value}
                            control={form.control}
                            name="analysts"
                            render={({ field }) => {
                              return (
                                <FormItem
                                  key={analyst.value}
                                  className="flex flex-row items-start space-x-3 space-y-0"
                                >
                                  <FormControl>
                                    <Checkbox
                                      checked={field.value?.includes(
                                        analyst.value
                                      )}
                                      onCheckedChange={(checked) => {
                                        return checked
                                          ? field.onChange([
                                              ...(field.value ?? []),
                                              analyst.value,
                                            ])
                                          : field.onChange(
                                              field.value?.filter(
                                                (value: string) =>
                                                  value !== analyst.value
                                              )
                                            );
                                      }}
                                    />
                                  </FormControl>
                                  <FormLabel className="font-normal cursor-pointer">
                                    {analyst.label}
                                  </FormLabel>
                                </FormItem>
                              );
                            }}
                          />
                        ))}
                      </div>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* 第一行：股票代碼、分析日期（2列） */}
              <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="ticker"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>股票代碼</FormLabel>
                      <FormControl>
                        <Input placeholder="NVDA" {...field} />
                      </FormControl>
                      <FormDescription>
                        輸入股票代碼（例如：NVDA、AAPL）
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="analysis_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>分析日期</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormDescription>選擇分析日期</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* 第二行：研究深度、快速思維模型、深層思維模型（3列） */}
              <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-3 gap-6">
                <FormField
                  control={form.control}
                  name="research_depth"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>研究深度</FormLabel>
                      <Select
                        onValueChange={(value) =>
                          field.onChange(parseInt(value))
                        }
                        defaultValue={field.value?.toString() ?? "3"}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="選擇研究深度" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent className="max-h-80">
                          <SelectItem value="1" className="py-3 cursor-pointer">
                            淺層 - 快速研究
                          </SelectItem>
                          <SelectItem value="3" className="py-3 cursor-pointer">
                            中等 - 適度討論
                          </SelectItem>
                          <SelectItem value="5" className="py-3 cursor-pointer">
                            深層 - 深入研究
                          </SelectItem>
                        </SelectContent>
                      </Select>
                      <FormDescription>選擇分析深度</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="quick_think_llm"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>快速思維模型</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="選擇模型" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {/* OpenAI */}
                          <SelectItem value="gpt-5.1-2025-11-13">
                            OpenAI: GPT-5.1
                          </SelectItem>
                          <SelectItem value="gpt-5-mini-2025-08-07">
                            OpenAI: GPT-5 Mini
                          </SelectItem>
                          <SelectItem value="gpt-5-nano-2025-08-07">
                            OpenAI: GPT-5 Nano
                          </SelectItem>
                          <SelectItem value="gpt-4.1-mini">
                            OpenAI: GPT-4.1 Mini
                          </SelectItem>
                          <SelectItem value="gpt-4.1-nano">
                            OpenAI: GPT-4.1 Nano
                          </SelectItem>
                          <SelectItem value="o4-mini-2025-04-16">
                            OpenAI: o4-mini
                          </SelectItem>

                          {/* Anthropic */}
                          <SelectItem value="claude-haiku-4-5-20251001">
                            Anthropic: Claude Haiku 4.5
                          </SelectItem>
                          <SelectItem value="claude-sonnet-4-5-20250929">
                            Anthropic: Claude Sonnet 4.5
                          </SelectItem>
                          <SelectItem value="claude-sonnet-4-0">
                            Anthropic: Claude Sonnet 4
                          </SelectItem>
                          <SelectItem value="claude-3-5-haiku-20241022">
                            Anthropic: Claude 3.5 Haiku
                          </SelectItem>
                          <SelectItem value="claude-3-haiku-20240307">
                            Anthropic: Claude 3 Haiku
                          </SelectItem>

                          {/* Google */}
                          <SelectItem value="gemini-2.5-pro">
                            Google: Gemini 2.5 Pro
                          </SelectItem>
                          <SelectItem value="gemini-2.5-flash">
                            Google: Gemini 2.5 Flash
                          </SelectItem>
                          <SelectItem value="gemini-2.5-flash-lite">
                            Google: Gemini 2.5 Flash Lite
                          </SelectItem>
                          <SelectItem value="gemini-2.0-flash">
                            Google: Gemini 2.0 Flash
                          </SelectItem>
                          <SelectItem value="gemini-2.0-flash-lite">
                            Google: Gemini 2.0 Flash Lite
                          </SelectItem>

                          {/* Grok */}
                          <SelectItem value="grok-4-1-fast-reasoning">
                            Grok: 4.1 Fast Reasoning
                          </SelectItem>
                          <SelectItem value="grok-4-1-fast-non-reasoning">
                            Grok: 4.1 Fast Non Reasoning
                          </SelectItem>
                          <SelectItem value="grok-4-fast-reasoning">
                            Grok: 4 Fast Reasoning
                          </SelectItem>
                          <SelectItem value="grok-4-fast-non-reasoning">
                            Grok: 4 Fast Non Reasoning
                          </SelectItem>
                          <SelectItem value="grok-4-0709">Grok: 4</SelectItem>
                          <SelectItem value="grok-3">Grok: 3</SelectItem>
                          <SelectItem value="grok-3-mini">
                            Grok: 3 Mini
                          </SelectItem>

                          {/* DeepSeek */}
                          <SelectItem value="deepseek-reasoner">
                            DeepSeek: Reasoner
                          </SelectItem>
                          <SelectItem value="deepseek-chat">
                            DeepSeek: Chat
                          </SelectItem>

                          {/* Qwen */}
                          <SelectItem value="qwen3-max">Qwen: 3 Max</SelectItem>
                          <SelectItem value="qwen-plus">Qwen: Plus</SelectItem>
                          <SelectItem value="qwen-flash">
                            Qwen: Flash
                          </SelectItem>
                        </SelectContent>
                      </Select>
                      <FormDescription>快速回應模型</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="deep_think_llm"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>深層思維模型</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="選擇模型" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {/* OpenAI */}
                          <SelectItem value="gpt-5.1-2025-11-13">
                            OpenAI: GPT-5.1
                          </SelectItem>
                          <SelectItem value="gpt-5-mini-2025-08-07">
                            OpenAI: GPT-5 Mini
                          </SelectItem>
                          <SelectItem value="gpt-5-nano-2025-08-07">
                            OpenAI: GPT-5 Nano
                          </SelectItem>
                          <SelectItem value="gpt-4.1-mini">
                            OpenAI: GPT-4.1 Mini
                          </SelectItem>
                          <SelectItem value="gpt-4.1-nano">
                            OpenAI: GPT-4.1 Nano
                          </SelectItem>
                          <SelectItem value="o4-mini-2025-04-16">
                            OpenAI: o4-mini
                          </SelectItem>

                          {/* Anthropic */}
                          <SelectItem value="claude-haiku-4-5-20251001">
                            Anthropic: Claude Haiku 4.5
                          </SelectItem>
                          <SelectItem value="claude-sonnet-4-5-20250929">
                            Anthropic: Claude Sonnet 4.5
                          </SelectItem>
                          <SelectItem value="claude-sonnet-4-0">
                            Anthropic: Claude Sonnet 4
                          </SelectItem>
                          <SelectItem value="claude-3-5-haiku-20241022">
                            Anthropic: Claude 3.5 Haiku
                          </SelectItem>
                          <SelectItem value="claude-3-haiku-20240307">
                            Anthropic: Claude 3 Haiku
                          </SelectItem>

                          {/* Google */}
                          <SelectItem value="gemini-2.5-pro">
                            Google: Gemini 2.5 Pro
                          </SelectItem>
                          <SelectItem value="gemini-2.5-flash">
                            Google: Gemini 2.5 Flash
                          </SelectItem>
                          <SelectItem value="gemini-2.5-flash-lite">
                            Google: Gemini 2.5 Flash Lite
                          </SelectItem>
                          <SelectItem value="gemini-2.0-flash">
                            Google: Gemini 2.0 Flash
                          </SelectItem>
                          <SelectItem value="gemini-2.0-flash-lite">
                            Google: Gemini 2.0 Flash Lite
                          </SelectItem>

                          {/* Grok */}
                          <SelectItem value="grok-4-1-fast-reasoning">
                            Grok: 4.1 Fast Reasoning
                          </SelectItem>
                          <SelectItem value="grok-4-1-fast-non-reasoning">
                            Grok: 4.1 Fast Non Reasoning
                          </SelectItem>
                          <SelectItem value="grok-4-fast-reasoning">
                            Grok: 4 Fast Reasoning
                          </SelectItem>
                          <SelectItem value="grok-4-fast-non-reasoning">
                            Grok: 4 Fast Non Reasoning
                          </SelectItem>
                          <SelectItem value="grok-4-0709">Grok: 4</SelectItem>
                          <SelectItem value="grok-3">Grok: 3</SelectItem>
                          <SelectItem value="grok-3-mini">
                            Grok: 3 Mini
                          </SelectItem>

                          {/* DeepSeek */}
                          <SelectItem value="deepseek-reasoner">
                            DeepSeek: Reasoner
                          </SelectItem>
                          <SelectItem value="deepseek-chat">
                            DeepSeek: Chat
                          </SelectItem>

                          {/* Qwen */}
                          <SelectItem value="qwen3-max">Qwen: 3 Max</SelectItem>
                          <SelectItem value="qwen-plus">Qwen: Plus</SelectItem>
                          <SelectItem value="qwen-flash">
                            Qwen: Flash
                          </SelectItem>
                        </SelectContent>
                      </Select>
                      <FormDescription>複雜推理模型</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* API Configuration Section */}
            <div className="space-y-4 border-t pt-6 mt-6">
              <h3 className="text-lg font-semibold">API 配置</h3>

              <FormField
                control={form.control}
                name="quick_think_base_url"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>快速思維模型 Base URL</FormLabel>
                    <Select
                      onValueChange={(value) => {
                        if (value !== "custom") {
                          field.onChange(value);
                        } else {
                          field.onChange(""); // Clear value for custom input
                        }
                      }}
                      defaultValue={
                        [
                          "https://api.openai.com/v1",
                          "https://api.anthropic.com/v1",
                          "https://api.x.ai/v1",
                          "https://api.deepseek.com/v1",
                          "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                        ].includes(field.value || "")
                          ? field.value
                          : "custom"
                      }
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="選擇 API 端點" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="https://api.openai.com/v1">
                          OpenAI (預設)
                        </SelectItem>
                        <SelectItem value="https://api.anthropic.com/v1">
                          Anthropic
                        </SelectItem>
                        <SelectItem value="https://generativelanguage.googleapis.com/v1beta/openai">
                          Google (Gemini)
                        </SelectItem>
                        <SelectItem value="https://api.x.ai/v1">
                          Grok (xAI)
                        </SelectItem>
                        <SelectItem value="https://api.deepseek.com/v1">
                          DeepSeek
                        </SelectItem>
                        <SelectItem value="https://dashscope-intl.aliyuncs.com/compatible-mode/v1">
                          Qwen (Alibaba)
                        </SelectItem>
                        <SelectItem value="custom">自訂端點</SelectItem>
                      </SelectContent>
                    </Select>

                    {(![
                      "https://api.openai.com/v1",
                      "https://api.anthropic.com/v1",
                      "https://generativelanguage.googleapis.com/v1beta/openai",
                      "https://api.x.ai/v1",
                      "https://api.deepseek.com/v1",
                      "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                    ].includes(field.value || "") ||
                      field.value === "") && (
                      <div className="mt-2">
                        <FormControl>
                          <Input
                            placeholder="請輸入自訂 Base URL"
                            value={field.value || ""}
                            onChange={field.onChange}
                          />
                        </FormControl>
                      </div>
                    )}

                    <FormDescription>
                      快速思維模型的 API 基礎網址
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="quick_think_api_key"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>快速思維模型 API Key</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="sk-..." {...field} />
                    </FormControl>
                    <FormDescription>
                      該模型的專屬 API Key（若留空則使用預設/環境變數）
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="deep_think_base_url"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>深層思維模型 Base URL</FormLabel>
                    <Select
                      onValueChange={(value) => {
                        if (value !== "custom") {
                          field.onChange(value);
                        } else {
                          field.onChange(""); // Clear value for custom input
                        }
                      }}
                      defaultValue={
                        [
                          "https://api.openai.com/v1",
                          "https://api.anthropic.com/v1",
                          "https://api.x.ai/v1",
                          "https://api.deepseek.com/v1",
                          "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                        ].includes(field.value || "")
                          ? field.value
                          : "custom"
                      }
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="選擇 API 端點" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="https://api.openai.com/v1">
                          OpenAI (預設)
                        </SelectItem>
                        <SelectItem value="https://api.anthropic.com/v1">
                          Anthropic
                        </SelectItem>
                        <SelectItem value="https://generativelanguage.googleapis.com/v1beta/openai">
                          Google (Gemini)
                        </SelectItem>
                        <SelectItem value="https://api.x.ai/v1">
                          Grok (xAI)
                        </SelectItem>
                        <SelectItem value="https://api.deepseek.com/v1">
                          DeepSeek
                        </SelectItem>
                        <SelectItem value="https://dashscope-intl.aliyuncs.com/compatible-mode/v1">
                          Qwen (Alibaba)
                        </SelectItem>
                        <SelectItem value="custom">自訂端點</SelectItem>
                      </SelectContent>
                    </Select>

                    {(![
                      "https://api.openai.com/v1",
                      "https://api.anthropic.com/v1",
                      "https://generativelanguage.googleapis.com/v1beta/openai",
                      "https://api.x.ai/v1",
                      "https://api.deepseek.com/v1",
                      "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                    ].includes(field.value || "") ||
                      field.value === "") && (
                      <div className="mt-2">
                        <FormControl>
                          <Input
                            placeholder="請輸入自訂 Base URL"
                            value={field.value || ""}
                            onChange={field.onChange}
                          />
                        </FormControl>
                      </div>
                    )}

                    <FormDescription>
                      深層思維模型的 API 基礎網址
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="deep_think_api_key"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>深層思維模型 API Key</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="sk-..." {...field} />
                    </FormControl>
                    <FormDescription>
                      該模型的專屬 API Key（若留空則使用預設/環境變數）
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="embedding_base_url"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>嵌入模型 Base URL</FormLabel>
                    <Select
                      onValueChange={(value) => {
                        if (value !== "custom") {
                          field.onChange(value);
                        } else {
                          field.onChange(""); // Clear value for custom input
                        }
                      }}
                      defaultValue={
                        field.value === "https://api.openai.com/v1" ||
                        !field.value
                          ? "https://api.openai.com/v1"
                          : "custom"
                      }
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="選擇嵌入模型端點" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="https://api.openai.com/v1">
                          OpenAI (預設)
                        </SelectItem>
                        <SelectItem value="custom">自訂端點</SelectItem>
                      </SelectContent>
                    </Select>

                    {field.value !== "https://api.openai.com/v1" && (
                      <div className="mt-2">
                        <FormControl>
                          <Input
                            placeholder="請輸入自訂 Base URL"
                            value={field.value || ""}
                            onChange={field.onChange}
                          />
                        </FormControl>
                      </div>
                    )}

                    <FormDescription>
                      嵌入向量生成的 API 端點（用於記憶體系統）
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="embedding_api_key"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>嵌入模型 API Key</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="sk-..." {...field} />
                    </FormControl>
                    <FormDescription>
                      該端點的 API Key（若留空則使用環境變數 OPENAI_API_KEY）
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="alpha_vantage_api_key"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Alpha Vantage API Key *</FormLabel>
                    <FormControl>
                      <Input
                        type="password"
                        placeholder="輸入 Alpha Vantage API Key（必填）"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      用於獲取市場基本面數據（必填）
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={loading}
              size="lg"
            >
              {loading ? "執行分析中..." : "執行分析"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
