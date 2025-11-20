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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { AnalysisRequest } from "@/lib/types";

const formSchema = z.object({
  ticker: z.string().min(1, "股票代碼為必填").max(10),
  analysis_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "日期格式必須為 YYYY-MM-DD"),
  analysts: z.array(z.string()).min(1, "請至少選擇一位分析師"),
  research_depth: z.number().int().min(1).max(5),
  shallow_thinking_agent: z.string().min(1, "請選擇快速思維模型"), 
  deep_thinking_agent: z.string().min(1, "請選擇深層思維模型"),
  
  // API Configuration
  openai_api_key: z.string().min(20, "請輸入有效的 OpenAI API Key"),
  openai_base_url: z.string().url("請輸入有效的 URL").optional().or(z.literal("")),
  alpha_vantage_api_key: z.string().optional().or(z.literal("")),
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
      shallow_thinking_agent: "gpt-4o-mini",
      deep_thinking_agent: "gpt-4o",
      openai_api_key: "",
      openai_base_url: "https://api.openai.com/v1",
      alpha_vantage_api_key: "",
    },
  });

  // 全選/取消全選
  const toggleSelectAll = () => {
    const currentAnalysts = form.getValues("analysts");
    if (currentAnalysts.length === ANALYSTS.length) {
      form.setValue("analysts", []);
    } else {
      form.setValue("analysts", ANALYSTS.map(a => a.value));
    }
  };

  function handleSubmit(values: z.infer<typeof formSchema>) {
    const request: AnalysisRequest = {
      ...values,
    };
    onSubmit(request);
  }

  return (
    <Card className="w-full shadow-lg">
      <CardHeader>
        <CardTitle>交易分析配置</CardTitle>
        <CardDescription>
          配置您的交易分析參數
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 分析師選擇區塊 */}
              <div className="md:col-span-2 border-b pb-6">
                <div className="flex justify-between items-center mb-4">
                  <FormLabel className="text-base font-semibold">分析師團隊</FormLabel>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={toggleSelectAll}
                  >
                    {form.watch("analysts").length === ANALYSTS.length ? "取消全選" : "全選"}
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
                                      checked={field.value?.includes(analyst.value)}
                                      onCheckedChange={(checked) => {
                                        return checked
                                          ? field.onChange([...field.value, analyst.value])
                                          : field.onChange(
                                              field.value?.filter(
                                                (value: string) => value !== analyst.value
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

              {/* 研究深度 - 放大顯示 */}
              <FormField
                control={form.control}
                name="research_depth"
                render={({ field }) => (
                  <FormItem className="md:col-span-2">
                    <FormLabel className="text-lg font-semibold">研究深度</FormLabel>
                    <Select
                      onValueChange={(value) => field.onChange(parseInt(value))}
                      defaultValue={field.value.toString()}
                    >
                      <FormControl>
                        <SelectTrigger className="h-12 text-base">
                          <SelectValue placeholder="選擇研究深度" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="1">淺層 - 快速研究，較少的辯論和策略討論</SelectItem>
                        <SelectItem value="3">中等 - 中等程度，適度的辯論和策略討論</SelectItem>
                        <SelectItem value="5">深層 - 全面研究，深入的辯論和策略討論</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      選擇分析的深度和完整性
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

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
                    <FormDescription>
                      選擇分析日期
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* 快速思維模型 */}
              <FormField
                control={form.control}
                name="shallow_thinking_agent"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>快速思維模型</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="選擇模型" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="gpt-5.1-2025-11-13">GPT-5.1</SelectItem>
                        <SelectItem value="gpt-5-mini-2025-08-07">GPT-5 Mini</SelectItem>
                        <SelectItem value="gpt-5-nano-2025-08-07">GPT-5 Nano</SelectItem>
                        <SelectItem value="gpt-4.1-mini">GPT-4.1 Mini</SelectItem>
                        <SelectItem value="gpt-4.1-nano">GPT-4.1 Nano</SelectItem>
                        <SelectItem value="gpt-4o">GPT-4o</SelectItem>
                        <SelectItem value="gpt-4o-mini">GPT-4o Mini</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      用於快速回應的模型
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* 深層思維模型 */}
              <FormField
                control={form.control}
                name="deep_thinking_agent"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>深層思維模型</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="選擇模型" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="gpt-5.1-2025-11-13">GPT-5.1</SelectItem>
                        <SelectItem value="gpt-5-mini-2025-08-07">GPT-5 Mini</SelectItem>
                        <SelectItem value="gpt-5-nano-2025-08-07">GPT-5 Nano</SelectItem>
                        <SelectItem value="gpt-4.1-mini">GPT-4.1 Mini</SelectItem>
                        <SelectItem value="gpt-4.1-nano">GPT-4.1 Nano</SelectItem>
                        <SelectItem value="gpt-4o">GPT-4o</SelectItem>
                        <SelectItem value="gpt-4o-mini">GPT-4o Mini</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      用於複雜推理的模型
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              

            </div>

            {/* API Configuration Section */}
            <div className="space-y-4 border-t pt-6 mt-6">
              <h3 className="text-lg font-semibold">API 配置</h3>
              
              <FormField
                control={form.control}
                name="openai_api_key"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>OpenAI API Key（必填）</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="sk-..." {...field} />
                    </FormControl>
                    <FormDescription>
                      您的 OpenAI API Key（用於 LLM 推理）
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="openai_base_url"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>OpenAI Base URL（選填）</FormLabel>
                    <FormControl>
                      <Input placeholder="https://api.openai.com/v1" {...field} />
                    </FormControl>
                    <FormDescription>
                      API 基礎網址（預設為 OpenAI 官方）
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
                    <FormLabel>Alpha Vantage API Key（選填）</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="選填，用於更詳細的數據" {...field} />
                    </FormControl>
                    <FormDescription>
                      用於獲取更詳細的財務數據（可選）
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading} size="lg">
              {loading ? "執行分析中..." : "執行分析"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
