"use client"

import { motion } from "framer-motion"
import { fadeInUp } from "@/lib/motion"
import { cn } from "@/lib/utils"

interface SectionHeaderProps {
  label?: string
  title: string
  description?: string
  className?: string
  align?: "left" | "center"
}

export function SectionHeader({
  label,
  title,
  description,
  className,
  align = "left",
}: SectionHeaderProps) {
  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-80px" }}
      className={cn(
        "mb-12 max-w-2xl",
        align === "center" && "mx-auto text-center",
        className
      )}
    >
      {label && (
        <span className="mb-3 inline-block text-xs font-semibold uppercase tracking-widest text-blinkit-green">
          {label}
        </span>
      )}
      <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
        {title}
      </h2>
      {description && (
        <p className="mt-4 text-base leading-relaxed text-muted-foreground sm:text-lg">
          {description}
        </p>
      )}
    </motion.div>
  )
}
