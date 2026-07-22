import { Header } from "@/components/layout/header"
import { Footer } from "@/components/layout/footer"
import { HeroSection } from "@/components/sections/hero-section"
import { ResearchSnapshot } from "@/components/sections/research-snapshot"
import { BehaviorFramework } from "@/components/sections/behavior-framework"
import { EvidenceExplorer } from "@/components/sections/evidence-explorer"
import { InsightsSection } from "@/components/sections/insights-section"
import { MethodologySection } from "@/components/sections/methodology-section"

export default function Home() {
  return (
    <>
      <Header />
      <main className="flex-1">
        <HeroSection />
        <ResearchSnapshot />
        <BehaviorFramework />
        <EvidenceExplorer />
        <InsightsSection />
        <MethodologySection />
      </main>
      <Footer />
    </>
  )
}
