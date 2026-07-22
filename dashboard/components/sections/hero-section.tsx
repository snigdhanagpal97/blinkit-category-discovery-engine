"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowRight, BookOpen } from "lucide-react"
import { Button } from "@/components/ui/button"
import { FunnelVisualization } from "@/components/cards/funnel-visualization"
import { fadeInUp } from "@/lib/motion"

export function HeroSection() {
  return (
    <section id="overview" className="relative overflow-hidden px-6 pb-24 pt-16 lg:px-8 lg:pb-32 lg:pt-24">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-32 right-0 size-[500px] rounded-full bg-blinkit-green/5 blur-3xl" />
        <div className="absolute -bottom-20 -left-20 size-[400px] rounded-full bg-blinkit-yellow/10 blur-3xl" />
      </div>

      <div className="relative mx-auto grid max-w-[1400px] items-center gap-16 lg:grid-cols-2 lg:gap-20">
        <div className="max-w-xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-white px-4 py-1.5 text-xs font-medium text-muted-foreground shadow-sm">
              <span className="size-1.5 rounded-full bg-blinkit-green" />
              Research Workspace · Q3 2026
            </span>
          </motion.div>

          <motion.h1
            variants={fadeInUp}
            initial="hidden"
            animate="visible"
            className="text-4xl font-semibold leading-[1.1] tracking-tight text-foreground sm:text-5xl lg:text-[3.25rem]"
          >
            Blinkit Category Discovery Engine
          </motion.h1>

          <motion.p
            variants={fadeInUp}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.1 }}
            className="mt-6 text-lg leading-relaxed text-muted-foreground sm:text-xl"
          >
            Understanding why high-frequency quick-commerce customers don&apos;t
            naturally expand beyond habitual grocery purchases into
            higher-consideration categories.
          </motion.p>

          <motion.div
            variants={fadeInUp}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.2 }}
            className="mt-10 flex flex-wrap items-center gap-3"
          >
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button
                size="lg"
                className="h-12 gap-2 rounded-2xl bg-blinkit-green px-6 text-sm font-semibold text-white shadow-md hover:bg-blinkit-green/90 hover:shadow-lg"
                render={<Link href="#research" />}
              >
                Explore Research
                <ArrowRight className="size-4" />
              </Button>
            </motion.div>

            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button
                variant="outline"
                size="lg"
                className="h-12 gap-2 rounded-2xl border-border bg-white px-6 text-sm font-semibold shadow-sm hover:bg-white hover:shadow-md"
                render={<Link href="#methodology" />}
              >
                <BookOpen className="size-4" />
                View Methodology
              </Button>
            </motion.div>
          </motion.div>
        </div>

        <div className="relative lg:pl-8">
          <div className="rounded-[20px] border border-border bg-white/60 p-2 shadow-[0_8px_32px_rgba(0,0,0,0.06)] backdrop-blur-sm">
            <FunnelVisualization />
          </div>
        </div>
      </div>
    </section>
  )
}
