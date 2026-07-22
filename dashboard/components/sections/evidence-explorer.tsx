"use client"

import { Search } from "lucide-react"
import { motion } from "framer-motion"
import { EvidenceCard } from "@/components/cards/evidence-card"
import { FilterSelect } from "@/components/ui/filter-select"
import { Input } from "@/components/ui/input"
import { SectionHeader } from "@/components/ui/section-header"
import { Switch } from "@/components/ui/switch"
import { evidenceData, filterOptions } from "@/lib/data"
import { fadeInUp, staggerContainer } from "@/lib/motion"

export function EvidenceExplorer() {
  return (
    <section id="evidence" className="px-6 py-24 lg:px-8 lg:py-32">
      <div className="mx-auto max-w-[1400px]">
        <SectionHeader
          label="Section 3"
          title="Evidence Explorer"
          description="Browse validated discovery signals from public conversations. Filter by platform, barrier, theme, or category."
        />

        <motion.div
          variants={fadeInUp}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-40px" }}
          className="mb-10 rounded-[20px] border border-border bg-white p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)]"
        >
          <div className="mb-5">
            <label className="mb-1.5 block text-xs font-medium text-muted-foreground">
              Search evidence
            </label>
            <div className="relative">
              <Search className="absolute top-1/2 left-4 size-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search quotes, themes, barriers..."
                className="h-11 rounded-2xl border-border bg-muted/20 pl-11 text-sm focus-visible:ring-blinkit-green/20"
              />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
            <FilterSelect label="Platform" options={filterOptions.platforms} />
            <FilterSelect label="Barrier" options={filterOptions.barriers} />
            <FilterSelect label="Theme" options={filterOptions.themes} />
            <FilterSelect label="Category" options={filterOptions.categories} />
            <Switch label="Discovery signals only" defaultChecked />
          </div>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-40px" }}
          className="grid gap-6 lg:grid-cols-3"
        >
          {evidenceData.map((evidence, index) => (
            <EvidenceCard key={evidence.id} evidence={evidence} index={index} />
          ))}
        </motion.div>
      </div>
    </section>
  )
}
