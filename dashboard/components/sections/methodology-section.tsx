"use client"

import { motion } from "framer-motion"
import {
  Database,
  Search,
  Tags,
  CheckCircle2,
  Lightbulb,
  ChevronDown,
} from "lucide-react"
import { SectionHeader } from "@/components/ui/section-header"
import { methodologySteps } from "@/lib/data"
import { fadeInUp } from "@/lib/motion"
import { cn } from "@/lib/utils"

const iconMap = {
  database: Database,
  search: Search,
  tags: Tags,
  "check-circle": CheckCircle2,
  lightbulb: Lightbulb,
}

export function MethodologySection() {
  return (
    <section id="methodology" className="px-6 py-24 lg:px-8 lg:py-32">
      <div className="mx-auto max-w-[1400px]">
        <SectionHeader
          label="Section 5"
          title="Methodology"
          description="Our five-stage research pipeline transforms raw public conversations into actionable product insights."
          align="center"
          className="mx-auto text-center"
        />

        <div className="relative mt-4">
          <div className="absolute top-12 right-0 left-0 hidden h-px bg-border lg:block" />

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-5 lg:gap-4">
            {methodologySteps.map((step, index) => {
              const Icon = iconMap[step.icon]
              return (
                <motion.div
                  key={step.title}
                  variants={fadeInUp}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: "-40px" }}
                  transition={{ delay: index * 0.1 }}
                  className="relative flex flex-col items-center text-center"
                >
                  <motion.div
                    whileHover={{ scale: 1.05, transition: { duration: 0.2 } }}
                    className={cn(
                      "relative z-10 mb-5 flex size-16 items-center justify-center rounded-[20px] border border-border bg-white",
                      "shadow-[0_4px_16px_rgba(0,0,0,0.06)]"
                    )}
                  >
                    <Icon className="size-6 text-blinkit-green" strokeWidth={1.75} />
                    <span className="absolute -top-2 -right-2 flex size-6 items-center justify-center rounded-full bg-blinkit-green text-[10px] font-bold text-white">
                      {index + 1}
                    </span>
                  </motion.div>

                  <h3 className="mb-2 text-base font-semibold text-foreground">
                    {step.title}
                  </h3>
                  <p className="max-w-[200px] text-sm leading-relaxed text-muted-foreground">
                    {step.description}
                  </p>

                  {index < methodologySteps.length - 1 && (
                    <div className="mt-4 flex flex-col items-center text-muted-foreground/40 lg:hidden">
                      <ChevronDown className="size-4" />
                    </div>
                  )}
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
