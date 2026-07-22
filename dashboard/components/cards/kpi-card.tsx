"use client"

import { motion } from "framer-motion"
import type { LucideIcon } from "lucide-react"
import { fadeInUp } from "@/lib/motion"
import { cn } from "@/lib/utils"

interface KpiCardProps {
  icon: LucideIcon
  title: string
  value: string
  description: string
  index?: number
}

export function KpiCard({
  icon: Icon,
  title,
  value,
  description,
  index = 0,
}: KpiCardProps) {
  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-40px" }}
      transition={{ delay: index * 0.08 }}
      whileHover={{
        y: -6,
        boxShadow: "0 20px 40px -12px rgba(12, 131, 31, 0.12)",
        transition: { duration: 0.25 },
      }}
      className={cn(
        "group relative flex flex-col gap-4 rounded-[20px] border border-border bg-white p-6",
        "shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)]"
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex size-11 items-center justify-center rounded-2xl bg-blinkit-green/8 text-blinkit-green transition-colors group-hover:bg-blinkit-green/12">
          <Icon className="size-5" strokeWidth={1.75} />
        </div>
      </div>

      <div className="space-y-1">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        <p className="text-4xl font-semibold tracking-tight text-foreground tabular-nums">
          {value}
        </p>
      </div>

      <p className="text-sm leading-relaxed text-muted-foreground">{description}</p>
    </motion.div>
  )
}
