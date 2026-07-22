"use client"

import { motion } from "framer-motion"
import { KpiCard } from "@/components/cards/kpi-card"
import { SectionHeader } from "@/components/ui/section-header"
import { kpiData } from "@/lib/data"
import { staggerContainer } from "@/lib/motion"

export function ResearchSnapshot() {
  return (
    <section id="research" className="px-6 py-24 lg:px-8 lg:py-32">
      <div className="mx-auto max-w-[1400px]">
        <SectionHeader
          label="Section 1"
          title="Research Snapshot"
          description="Key metrics from our discovery pipeline — from raw public conversations to validated behavioral signals."
        />

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4"
        >
          {kpiData.map((kpi, index) => (
            <KpiCard key={kpi.title} {...kpi} index={index} />
          ))}
        </motion.div>
      </div>
    </section>
  )
}
