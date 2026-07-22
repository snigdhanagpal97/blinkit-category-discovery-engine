"use client"

import { motion } from "framer-motion"
import { ChevronDown } from "lucide-react"
import { FrameworkCard } from "@/components/cards/framework-card"
import { SectionHeader } from "@/components/ui/section-header"
import { frameworkSteps } from "@/lib/data"
import { fadeInUp } from "@/lib/motion"

export function BehaviorFramework() {
  return (
    <section className="px-6 py-24 lg:px-8 lg:py-32">
      <div className="mx-auto max-w-[1400px]">
        <SectionHeader
          label="Section 2"
          title="Behavior Framework"
          description="A three-stage model mapping how quick-commerce customers move from unawareness to confident category expansion."
        />

        <div className="flex flex-col gap-4 lg:flex-row lg:items-stretch">
          {frameworkSteps.map((step, index) => (
            <FrameworkCard
              key={step.stage}
              {...step}
              index={index}
              isLast={index === frameworkSteps.length - 1}
            />
          ))}
        </div>

        <motion.div
          variants={fadeInUp}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="mt-6 flex justify-center lg:hidden"
        >
          <div className="flex flex-col items-center gap-1 text-muted-foreground/50">
            <ChevronDown className="size-4" />
            <ChevronDown className="size-4 -mt-2" />
          </div>
        </motion.div>
      </div>
    </section>
  )
}
