"use client"

import { motion } from "framer-motion"
import { OpportunityCard } from "@/components/cards/opportunity-card"
import { SectionHeader } from "@/components/ui/section-header"
import { insightsData } from "@/lib/data"
import { staggerContainer } from "@/lib/motion"

export function InsightsSection() {
  return (
    <section id="insights" className="px-6 py-24 lg:px-8 lg:py-32">
      <div className="mx-auto max-w-[1400px]">
        <SectionHeader
          label="Section 4"
          title="Insights"
          description="Synthesized opportunities derived from validated behavioral signals — each with a clear product direction and business impact."
        />

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-40px" }}
          className="grid gap-6 lg:grid-cols-3"
        >
          {insightsData.map((insight, index) => (
            <OpportunityCard key={insight.id} insight={insight} index={index} />
          ))}
        </motion.div>
      </div>
    </section>
  )
}
