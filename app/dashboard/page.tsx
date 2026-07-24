"use client";
import React, { useState, useMemo, useEffect } from "react";
import { BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import Papa from "papaparse";

interface Feedback {
  uid: string;
  platform: string;
  source: string;
  text: string;
  rating: number;
  date: string;
}

interface EnrichedFeedback extends Feedback {
  sentiment: string;
  primary_theme: string;
  consideration_level: string;
  representative_quote: string;
}

const THEME_TO_BARRIER: Record<string, string> = {
  trust_quality: "CONFIDENCE",
  delivery_ops: "CONSIDER",
  returns_support: "CONFIDENCE",
  assortment_gap: "KNOW",
  price_value: "CONSIDER",
  app_ux: "CONSIDER",
  habit_convenience: "CONSIDER",
  other: "OTHER",
};

const BARRIER_COLORS = {
  KNOW: "#256FEF",
  CONSIDER: "#F8CB46",
  CONFIDENCE: "#0C831F",
  OTHER: "#9CA3AF",
};

export default function Dashboard() {
  const [allFeedback, setAllFeedback] = useState<Feedback[]>([]);
  const [enrichedFeedback, setEnrichedFeedback] = useState<EnrichedFeedback[]>([]);
  const [dateRange, setDateRange] = useState({ start: "", end: "" });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDemoData();
  }, []);

  const loadDemoData = async () => {
    setLoading(true);
    try {
      const sampleFeedback: Feedback[] = [{
        uid: "1",
        platform: "blinkit",
        source: "playstore",
        text: "Great service, fast delivery!",
        rating: 5,
        date: "2026-07-20",
      }];
      setAllFeedback(sampleFeedback);
      setEnrichedFeedback(sampleFeedback.map((f) => ({
        ...f,
        sentiment: f.rating >= 4 ? "positive" : f.rating <= 2 ? "negative" : "neutral",
        primary_theme: "delivery_ops",
        consideration_level: "high",
        representative_quote: f.text,
      })));
    } catch (error) {
      console.error("Error loading demo data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (file: File) => {
    setLoading(true);
    Papa.parse(file, {
      header: true,
      complete: (results) => {
        const data = results.data.filter((row: any) => row.uid) as Feedback[];
        setAllFeedback(data);
        const enriched = data.map((f) => ({
          ...f,
          sentiment: (f as any).sentiment || "unknown",
          primary_theme: (f as any).primary_theme || "other",
          consideration_level: (f as any).consideration_level || "unknown",
          representative_quote: (f as any).representative_quote || f.text,
        }));
        setEnrichedFeedback(enriched);
        setLoading(false);
      },
      error: () => {
        console.error("CSV parse error");
        setLoading(false);
      },
    });
  };

  const filteredData = useMemo(() => {
    return enrichedFeedback.filter((item) => {
      if (!dateRange.start || !dateRange.end) return true;
      const itemDate = new Date(item.date);
      return itemDate >= new Date(dateRange.start) && itemDate <= new Date(dateRange.end);
    });
  }, [enrichedFeedback, dateRange]);

  const metrics = useMemo(() => {
    const total = filteredData.length;
    const avgRating = total > 0 ? (filteredData.reduce((sum, f) => sum + f.rating, 0) / total).toFixed(2) : "0";
    const positiveSentiment = filteredData.filter((f) => f.sentiment === "positive").length;
    return {
      total,
      avgRating,
      positiveSentiment,
      sentimentRate: total > 0 ? Math.round((positiveSentiment / total) * 100) : 0,
    };
  }, [filteredData]);

  const confidenceData = useMemo(() => {
    const distribution: Record<string, number> = { High: 0, Medium: 0, Low: 0 };
    filteredData.forEach((f) => {
      const level = f.consideration_level.toLowerCase() === "high" ? "High" : f.consideration_level.toLowerCase() === "medium" ? "Medium" : "Low";
      distribution[level]++;
    });
    return Object.entries(distribution).map(([name, value]) => ({
      name,
      value,
      fill: name === "High" ? "#0C831F" : name === "Medium" ? "#F8CB46" : "#9CA3AF",
    }));
  }, [filteredData]);

  const barrierData = useMemo(() => {
    const barriers: Record<string, number> = { KNOW: 0, CONSIDER: 0, CONFIDENCE: 0, OTHER: 0 };
    filteredData.forEach((f) => {
      const barrier = THEME_TO_BARRIER[f.primary_theme] || "OTHER";
      barriers[barrier]++;
    });
    return Object.entries(barriers).map(([name, value]) => ({ name, value }));
  }, [filteredData]);

  const sentimentTimeline = useMemo(() => {
    const byDate: Record<string, { positive: number; neutral: number; negative: number }> = {};
    filteredData.forEach((f) => {
      const date = f.date.split("T")[0];
      if (!byDate[date]) byDate[date] = { positive: 0, neutral: 0, negative: 0 };
      byDate[date][f.sentiment as keyof typeof byDate[string]]++;
    });
    return Object.entries(byDate).sort(([a], [b]) => a.localeCompare(b)).map(([date, counts]) => ({
      date,
      positive: counts.positive,
      neutral: counts.neutral,
      negative: counts.negative,
    }));
  }, [filteredData]);

  const wordCloudData = useMemo(() => {
    const themes: Record<string, number> = {};
    filteredData.forEach((f) => {
      themes[f.primary_theme] = (themes[f.primary_theme] || 0) + 1;
    });
    return Object.entries(themes).sort(([, a], [, b]) => b - a).slice(0, 10).map(([word, freq]) => ({
      word: word.replace(/_/g, " ").toUpperCase(),
      freq,
      size: Math.max(12, Math.min(32, 12 + freq / 2)),
    }));
  }, [filteredData]);

  return (
    <div className="min-h-screen bg-[#FBFAF3]">
      <header className="bg-white border-b border-[#E8E6DC] sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#F8CB46] rounded-lg flex items-center justify-center">
                <span className="text-lg font-bold text-[#1A1A1A]">📊</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-[#1A1A1A]">Blinkit Flash</h1>
                <p className="text-sm text-[#6B7280]">Discovery Engine Analytics</p>
              </div>
            </div>
            <label className="px-4 py-2 bg-[#0C831F] text-white rounded-lg cursor-pointer hover:bg-[#0a6a28] transition">
              Upload CSV
              <input type="file" accept=".csv" onChange={(e) => { if (e.target.files?.[0]) handleFileUpload(e.target.files[0]); }} className="hidden" />
            </label>
          </div>
          <div className="flex gap-4 mt-4">
            <div>
              <label className="block text-xs font-semibold text-[#6B7280] mb-1">Start Date</label>
              <input type="date" value={dateRange.start} onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })} className="px-3 py-2 borderorder-[#E8E6DC] rounded-lg text-sm" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-[#6B7280] mb-1">End Date</label>
              <input type="date" value={dateRange.end} onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })} className="px-3 py-2 border border-[#E8E6DC] rounded-lg text-sm" />
            </div>
            <div className="flex items-end">
              <button onClick={() => setDateRange({ start: "", end: "" })} className="px-4 py-2 text-sm text-[#6B7280] hover:bg-[#F9F9F9] rounded-lg transition">Clear</button>
            </div>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-6 py-8">
        {loading ? <div className="flex items-center justify-center h-96"><p className="text-[#6B7280]">Loading...</p></div> : filteredData.length === 0 ? (
          <div className="bg-white rounded-lg border border-[#E8E6DC] p-8 text-center">
            <p className="text-[#6B7280] mb-4">Upload CSV to begin</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <MetricCard label="Total Reviews" value={metrics.total} subtext="analyzed" />
              <MetricCard label="Avg Rating" value={metrics.avgRating} subtext="out of 5" />
              <MetricCard label="Sentiment" value={`${metrics.sentimentRate}%`} subtext="positive" />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <ChartCard title="Confidence Distribution">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={confidenceData} cx="50%" cy="50%" outerRadius={80} dataKey="value">
                      {confidenceData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.fill} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </ChartCard>
              <ChartCard title="Barrier Breakdown">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={barrierData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E8E6DC" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#0C831F" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>
            <ChartCard title="Sentiment Over Time" className="mb-8">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={sentimentTimeline}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E8E6DC" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="positive" stroke="#0C831F" strokeWidth={2} />
                  <Line type="monotone" dataKey="neutral" stroke="#F8CB46" strokeWidth={2} />
                  <Line type="monotone" dataKey="negative" stroke="#D32F2F" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>
            <ChartCard title="Discovery Signals">
              <div className="flex flex-wrap gap-3 p-4">
                {wordCloudData.map((item) => (
                  <span key={item.word} style={{ fontSize: `${item.size}px` }} className="text-[#0C831F] font-bold opacity-75 hover:opacity-100 transition">
                    {item.word}
                  </span>
                ))}
              </div>
            </ChartCard>
          </>
        )}
      </main>
    </div>
  );
}

function MetricCard({ label, value, subtext }: { label: string; value: string | number; subtext: string }) {
  return (
    <div className="bg-white rounded-lg border border-[#E8E6DC] p-6">
      <p className="text-sm text-[#6B7280] font-semibold mb-2">{label}</p>
      <p className="text-3xl font-bold text-[#1A1A1A]">{value}</p>
      <p className="text-xs text-[#9CA3AF] mt-1">{subtext}</p>
    </div>
  );
}

function ChartCard({ title, children, className = "" }: { title: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white rounded-lg border border-[#E8E6DC] p-6 ${className}`}>
      <h2 className="text-lg font-bold text-[#1A1A1A] mb-4">{title}</h2>
      {children}
    </div>
  );
}
