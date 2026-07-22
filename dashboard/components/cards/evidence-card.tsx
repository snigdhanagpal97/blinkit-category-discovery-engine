"use client"

import { motion } from "framer-motion"
import { ChevronDown, Quote } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { fadeInUp } from "@/lib/motion"
import type { EvidenceItem } from "@/lib/data"
import { cn } from "@/lib/utils"

const confidenceStyles = {
  High: "bg-blinkit-green/10 text-blinkit-green border-blinkit-green/20",
  Medium: "bg-blinkit-yellow/25 text-[#92700C] border-blinkit-yellow/40",
  Low: "bg-muted text-muted-foreground border-border",
}

interface EvidenceCardProps {
  evidence: EvidenceItem
  index?: number
}

export function EvidenceCard({ evidence, index = 0 }: EvidenceCardProps) {
  return (
    <motion.article
      variants={fadeInUp}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-40px" }}
      transition={{ delay: index * 0.1 }}
      whileHover={{
        y: -4,
        boxShadow: "0 20px 40px -12px rgba(0,0,0,0.08)",
        transition: { duration: 0.25 },
      }}
      className={cn(
        "flex flex-col rounded-[20px] border border-border bg-white",
        "shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)]"
      )}
    >
      <div className="flex flex-1 flex-col p-6 sm:p-8">
        <div className="mb-5 flex items-center justify-between gap-3">
          <Badge
            variant="outline"
            className="rounded-xl border-border bg-muted/50 px-3 py-1 text-xs font-medium"
          >
            {evidence.platform}
          </Badge>
          <span
            className={cn(
              "rounded-xl border px-2.5 py-1 text-xs font-semibold",
              confidenceStyles[evidence.confidence]
            )}
          >
            {evidence.confidence} confidence
          </span>
        </div>

        <div className="relative mb-6 flex-1">
          <Quote className="absolute -top-1 -left-1 size-8 text-blinkit-green/15" />
          <blockquote className="relative pl-6 text-base leading-relaxed text-foreground italic">
            &ldquo;{evidence.quote}&rdquo;
          </blockquote>
        </div>

        <div className="flex flex-wrap gap-2">
          <Tag label="Theme" value={evidence.theme} />
          <Tag label="Barrier" value={evidence.barrier} />
          <Tag label="JTBD" value={evidence.jtbd} accent />
        </div>
      </div>

      <div className="flex items-center justify-between border-t border-border px-6 py-4 sm:px-8">
        <span className="text-xs text-muted-foreground">Signal #{evidence.id}</span>
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Button
            variant="ghost"
            size="sm"
            className="gap-1.5 rounded-xl text-muted-foreground hover:text-foreground"
          >
            Expand
            <ChevronDown className="size-4" />
          </Button>
        </motion.div>
      </div>
    </motion.article>
  )
}

function Tag({
  label,
  value,
  accent = false,
}: {
  label: string
  value: string
  accent?: boolean
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs",
        accent
          ? "border-blinkit-green/20 bg-blinkit-green/5 text-blinkit-green"
          : "border-border bg-muted/30 text-muted-foreground"
      )}
    >
      <span className="font-medium opacity-60">{label}</span>
      <span className="font-semibold text-foreground">{value}</span>
    </span>
  )
}
