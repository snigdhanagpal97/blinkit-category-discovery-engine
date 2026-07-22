"use client"

import { motion } from "framer-motion"
import { ArrowUpRight, Lightbulb, Target, TrendingUp, AlertCircle } from "lucide-react"
import { fadeInUp } from "@/lib/motion"
import type { InsightItem } from "@/lib/data"
import { cn } from "@/lib/utils"

interface OpportunityCardProps {
  insight: InsightItem
  index?: number
}

const fields = [
  { key: "problem" as const, label: "Problem", icon: AlertCircle, color: "text-red-500/80" },
  { key: "opportunity" as const, label: "Opportunity", icon: Lightbulb, color: "text-blinkit-yellow" },
  { key: "productDirection" as const, label: "Potential Product Direction", icon: Target, color: "text-blinkit-green" },
  { key: "businessImpact" as const, label: "Business Impact", icon: TrendingUp, color: "text-blinkit-green" },
]

export function OpportunityCard({ insight, index = 0 }: OpportunityCardProps) {
  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-40px" }}
      transition={{ delay: index * 0.1 }}
      whileHover={{
        y: -4,
        boxShadow: "0 20px 40px -12px rgba(12, 131, 31, 0.1)",
        transition: { duration: 0.25 },
      }}
      className={cn(
        "group flex flex-col rounded-[20px] border border-border bg-white",
        "shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)]"
      )}
    >
      <div className="flex items-center justify-between border-b border-border px-6 py-4">
        <span className="text-xs font-semibold uppercase tracking-widest text-blinkit-green">
          Opportunity {index + 1}
        </span>
        <ArrowUpRight className="size-4 text-muted-foreground/40 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-blinkit-green" />
      </div>

      <div className="flex flex-1 flex-col gap-5 p-6">
        {fields.map(({ key, label, icon: Icon, color }) => (
          <div key={key} className="space-y-1.5">
            <div className="flex items-center gap-2">
              <Icon className={cn("size-3.5", color)} strokeWidth={2} />
              <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                {label}
              </span>
            </div>
            <p className="text-sm leading-relaxed text-foreground">{insight[key]}</p>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
