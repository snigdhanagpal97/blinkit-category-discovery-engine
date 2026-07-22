"use client"

import { motion } from "framer-motion"
import { ArrowRight } from "lucide-react"
import { fadeInUp } from "@/lib/motion"
import { cn } from "@/lib/utils"

interface FrameworkCardProps {
  stage: string
  title: string
  description: string
  accent: "green" | "yellow"
  index: number
  isLast?: boolean
}

export function FrameworkCard({
  stage,
  title,
  description,
  accent,
  index,
  isLast = false,
}: FrameworkCardProps) {
  return (
    <div className="flex flex-1 items-stretch">
      <motion.div
        variants={fadeInUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-40px" }}
        transition={{ delay: index * 0.12 }}
        whileHover={{
          y: -4,
          boxShadow: "0 16px 32px -8px rgba(0,0,0,0.08)",
          transition: { duration: 0.25 },
        }}
        className={cn(
          "relative flex flex-1 flex-col rounded-[20px] border border-border bg-white p-8",
          "shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)]"
        )}
      >
        <span
          className={cn(
            "mb-6 inline-flex w-fit rounded-xl px-3 py-1 text-xs font-bold tracking-widest",
            accent === "green"
              ? "bg-blinkit-green/10 text-blinkit-green"
              : "bg-blinkit-yellow/30 text-[#92700C]"
          )}
        >
          {stage}
        </span>

        <h3 className="mb-3 text-xl font-semibold tracking-tight text-foreground">
          {title}
        </h3>
        <p className="text-sm leading-relaxed text-muted-foreground">{description}</p>
      </motion.div>

      {!isLast && (
        <div className="hidden shrink-0 flex-col items-center justify-center px-3 lg:flex">
          <ArrowRight className="size-5 text-muted-foreground/40" />
        </div>
      )}
    </div>
  )
}
