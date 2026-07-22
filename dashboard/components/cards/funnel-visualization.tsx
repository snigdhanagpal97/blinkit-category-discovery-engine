"use client"

import { motion } from "framer-motion"
import { ChevronDown } from "lucide-react"
import { fadeInUp } from "@/lib/motion"
import { cn } from "@/lib/utils"

const stages = [
  {
    label: "Awareness",
    sublabel: "Category visibility",
    color: "bg-blinkit-green/10 border-blinkit-green/20 text-blinkit-green",
    dot: "bg-blinkit-green",
    width: "w-[85%]",
  },
  {
    label: "Consideration",
    sublabel: "Mental availability",
    color: "bg-blinkit-yellow/20 border-blinkit-yellow/40 text-[#92700C]",
    dot: "bg-blinkit-yellow",
    width: "w-[65%]",
  },
  {
    label: "Confidence",
    sublabel: "Purchase readiness",
    color: "bg-blinkit-green/10 border-blinkit-green/20 text-blinkit-green",
    dot: "bg-blinkit-green",
    width: "w-[45%]",
  },
]

export function FunnelVisualization() {
  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.7, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
      className="relative flex flex-col items-center gap-0"
    >
      <div className="absolute inset-0 rounded-[20px] bg-gradient-to-br from-blinkit-green/5 via-transparent to-blinkit-yellow/10" />

      <div className="relative w-full space-y-0 p-8">
        {stages.map((stage, index) => (
          <div key={stage.label} className="flex flex-col items-center">
            <motion.div
              variants={fadeInUp}
              initial="hidden"
              animate="visible"
              transition={{ delay: 0.5 + index * 0.15 }}
              whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
              className={cn(
                "relative w-full rounded-[20px] border p-5 shadow-sm transition-shadow hover:shadow-md",
                stage.color,
                stage.width,
                index === 0 && "mx-auto",
                index === 1 && "mx-auto",
                index === 2 && "mx-auto"
              )}
            >
              <div className="flex items-center gap-3">
                <span className={cn("size-2.5 shrink-0 rounded-full", stage.dot)} />
                <div>
                  <p className="text-sm font-semibold">{stage.label}</p>
                  <p className="text-xs opacity-70">{stage.sublabel}</p>
                </div>
              </div>

              {index < stages.length - 1 && (
                <div className="absolute -bottom-5 left-1/2 z-10 flex -translate-x-1/2 flex-col items-center">
                  <div className="h-5 w-px bg-border" />
                  <ChevronDown className="size-4 text-muted-foreground/60" />
                </div>
              )}
            </motion.div>

            {index < stages.length - 1 && <div className="h-5" />}
          </div>
        ))}
      </div>

      <div className="absolute -right-4 -top-4 size-24 rounded-full bg-blinkit-yellow/20 blur-2xl" />
      <div className="absolute -bottom-6 -left-6 size-32 rounded-full bg-blinkit-green/10 blur-3xl" />
    </motion.div>
  )
}
