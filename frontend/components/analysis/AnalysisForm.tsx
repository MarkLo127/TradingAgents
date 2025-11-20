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
  research_depth: z.number().min(1).max(5),
  deep_think_llm: z.string(), 
  quick_think_llm: z.string(),
});

interface AnalysisFormProps {
  onSubmit: (data: AnalysisRequest) => void;
  loading?: boolean;
}

export function AnalysisForm({ onSubmit, loading = false }: AnalysisFormProps) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      ticker: "NVDA",
      analysis_date: format(new Date(), "yyyy-MM-dd"),
      research_depth: 1,
      deep_think_llm: "gpt-4o-mini",
      quick_think_llm: "gpt-4o-mini",
    },
  });

  function handleSubmit(values: z.infer<typeof formSchema>) {
    const request: AnalysisRequest = {
      ...values,
      analysts: ["market", "sentiment", "news", "fundamentals"],
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

              <FormField
                control={form.control}
                name="research_depth"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>研究深度</FormLabel>
                    <Select
                      onValueChange={(value) => field.onChange(parseInt(value))}
                      defaultValue={field.value.toString()}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="選擇深度" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="1">1 - 快速</SelectItem>
                        <SelectItem value="2">2 - 標準</SelectItem>
                        <SelectItem value="3">3 - 詳盡</SelectItem>
                        <SelectItem value="4">4 - 深入</SelectItem>
                        <SelectItem value="5">5 - 全面</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      深度越高 = 辯論回合越多
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="deep_think_llm"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>深度思考模型</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="選擇模型" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="gpt-4o">GPT-4o</SelectItem>
                        <SelectItem value="gpt-4o-mini">GPT-4o Mini</SelectItem>
                        <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
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

            <Button type="submit" className="w-full" disabled={loading} size="lg">
              {loading ? "執行分析中..." : "執行分析"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
