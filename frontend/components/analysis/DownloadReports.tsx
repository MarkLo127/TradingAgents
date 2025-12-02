/**
 * Download Reports Component
 * Allows users to select and download analyst reports
 */
"use client";

import { useState } from "react";
import { Download, FileDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

interface AnalystInfo {
  key: string;
  label: string;
  reportKey: string;
  description: string;
}

interface DownloadReportsProps {
  ticker: string;
  analysisDate: string;
  taskId: string;
  analysts: AnalystInfo[];
  reports: any;
}

export function DownloadReports({
  ticker,
  analysisDate,
  taskId,
  analysts,
  reports,
}: DownloadReportsProps) {
  const [selectedAnalysts, setSelectedAnalysts] = useState<string[]>([]);
  const [isDownloading, setIsDownloading] = useState(false);

  // Helper to get nested value from reports object
  const getNestedValue = (obj: any, path: string) => {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  };

  // Filter analysts that have actual reports
  const availableAnalysts = analysts.filter(analyst => {
    const reportContent = getNestedValue(reports, analyst.reportKey);
    return reportContent && reportContent.trim().length > 0;
  });

  // Handle select all
  const handleSelectAll = () => {
    if (selectedAnalysts.length === availableAnalysts.length) {
      setSelectedAnalysts([]);
    } else {
      setSelectedAnalysts(availableAnalysts.map(a => a.key));
    }
  };

  // Handle individual selection
  const handleToggleAnalyst = (analystKey: string) => {
    setSelectedAnalysts(prev => {
      if (prev.includes(analystKey)) {
        return prev.filter(key => key !== analystKey);
      } else {
        return [...prev, analystKey];
      }
    });
  };

  // Handle download
  const handleDownload = async () => {
    if (selectedAnalysts.length === 0) return;

    setIsDownloading(true);
    try {
      const response = await fetch('/api/download/reports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ticker,
          analysis_date: analysisDate,
          task_id: taskId,
          analysts: selectedAnalysts,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || `下載失敗 (${response.status})`;
        throw new Error(errorMessage);
      }

      // Get the blob
      const blob = await response.blob();
      
      // Get filename from Content-Disposition header if available
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `${ticker}_${analysisDate}.pdf`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=(.+)/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      } else if (selectedAnalysts.length > 1) {
        filename = `${ticker}_${analysisDate}.zip`;
      }

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('Download error:', error);
      alert(error.message || '下載失敗，請稍後再試');
    } finally {
      setIsDownloading(false);
    }
  };

  if (availableAnalysts.length === 0) {
    return null;
  }

  const isAllSelected = selectedAnalysts.length === availableAnalysts.length && availableAnalysts.length > 0;

  return (
    <Card className="hover-lift animate-scale-up">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileDown className="h-5 w-5" />
          下載報告
        </CardTitle>
        <CardDescription>
          選擇要下載的分析師報告（支援單一PDF或多個ZIP）
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Select All */}
        <div className="flex items-center space-x-2 pb-2 border-b">
          <Checkbox
            id="select-all"
            checked={isAllSelected}
            onCheckedChange={handleSelectAll}
          />
          <Label
            htmlFor="select-all"
            className="text-sm font-medium cursor-pointer"
          >
            全選 ({availableAnalysts.length} 個報告)
          </Label>
        </div>

        {/* Analyst List */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {availableAnalysts.map(analyst => (
            <div
              key={analyst.key}
              className="flex items-start space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors"
            >
              <Checkbox
                id={`analyst-${analyst.key}`}
                checked={selectedAnalysts.includes(analyst.key)}
                onCheckedChange={() => handleToggleAnalyst(analyst.key)}
              />
              <div className="flex-1">
                <Label
                  htmlFor={`analyst-${analyst.key}`}
                  className="text-sm font-medium cursor-pointer"
                >
                  {analyst.label}
                </Label>
                <p className="text-xs text-muted-foreground mt-1">
                  {analyst.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Download Button */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="text-sm text-muted-foreground">
            已選擇 {selectedAnalysts.length} 個報告
          </div>
          <Button
            onClick={handleDownload}
            disabled={selectedAnalysts.length === 0 || isDownloading}
            className="gap-2"
          >
            <Download className="h-4 w-4" />
            {isDownloading ? '下載中...' : selectedAnalysts.length === 1 ? '下載 PDF' : '下載 ZIP'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
