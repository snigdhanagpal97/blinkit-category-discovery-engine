import {
  MessageSquare,
  Search,
  Sparkles,
  Layers,
  type LucideIcon,
} from "lucide-react"

export const navLinks = [
  { label: "Overview", href: "#overview" },
  { label: "Research", href: "#research" },
  { label: "Evidence", href: "#evidence" },
  { label: "Insights", href: "#insights" },
  { label: "Methodology", href: "#methodology" },
] as const

export interface KpiItem {
  icon: LucideIcon
  title: string
  value: string
  description: string
}

export const kpiData: KpiItem[] = [
  {
    icon: MessageSquare,
    title: "Public Conversations",
    value: "3,776",
    description: "Reddit & forum threads analyzed across 12 subreddits",
  },
  {
    icon: Search,
    title: "Retrieved Candidates",
    value: "674",
    description: "Evidence snippets matching discovery signal patterns",
  },
  {
    icon: Sparkles,
    title: "Validated Discovery Signals",
    value: "20",
    description: "Human-reviewed signals with high confidence scores",
  },
  {
    icon: Layers,
    title: "Behavioral Themes",
    value: "6",
    description: "Cross-cutting patterns in category expansion behavior",
  },
]

export const frameworkSteps = [
  {
    stage: "KNOW",
    title: "Awareness Gap",
    description:
      "Customers are unaware Blinkit carries certain categories beyond daily groceries.",
    accent: "green" as const,
  },
  {
    stage: "CONSIDER",
    title: "Mental Availability",
    description:
      "Customers know Blinkit sells them but don't naturally think of Blinkit first.",
    accent: "yellow" as const,
  },
  {
    stage: "CONFIDENCE",
    title: "Decision Support",
    description:
      "Customers hesitate because higher-consideration purchases require richer decision support.",
    accent: "green" as const,
  },
]

export interface EvidenceItem {
  id: string
  platform: string
  quote: string
  theme: string
  barrier: string
  jtbd: string
  confidence: "High" | "Medium" | "Low"
}

export const evidenceData: EvidenceItem[] = [
  {
    id: "ev-1",
    platform: "Reddit",
    quote:
      "I had no idea Blinkit even sold electronics accessories. I always just use it for milk and bread — never thought to browse beyond groceries.",
    theme: "Category Awareness",
    barrier: "Unaware of assortment",
    jtbd: "Discover non-grocery categories",
    confidence: "High",
  },
  {
    id: "ev-2",
    platform: "Twitter/X",
    quote:
      "For urgent groceries, Blinkit is my go-to. But for skincare or home decor? I'd still open Amazon or Nykaa — Blinkit doesn't come to mind.",
    theme: "Mental Availability",
    barrier: "Habitual grocery framing",
    jtbd: "Expand purchase occasions",
    confidence: "High",
  },
  {
    id: "ev-3",
    platform: "Reddit",
    quote:
      "I'd buy a phone charger on Blinkit if I could see reviews and compare brands. Right now there's not enough info to trust a ₹800 purchase.",
    theme: "Decision Confidence",
    barrier: "Insufficient product context",
    jtbd: "Make informed higher-ticket choices",
    confidence: "Medium",
  },
]

export interface InsightItem {
  id: string
  problem: string
  opportunity: string
  productDirection: string
  businessImpact: string
}

export const insightsData: InsightItem[] = [
  {
    id: "ins-1",
    problem:
      "Users mentally bucket Blinkit as a '10-minute grocery app' and never explore adjacent categories.",
    opportunity:
      "Surface category breadth at moments of high intent without disrupting the grocery habit loop.",
    productDirection:
      "Contextual category discovery modules on order confirmation and post-delivery screens.",
    businessImpact:
      "Increase AOV by 18–25% through cross-category attach on existing high-frequency users.",
  },
  {
    id: "ins-2",
    problem:
      "Higher-consideration categories lack the social proof and comparison tools users expect.",
    opportunity:
      "Adapt lightweight review and 'popular in your area' signals from quick-commerce context.",
    productDirection:
      "Micro-reviews, neighbor purchase counts, and curated 'staff picks' for non-grocery SKUs.",
    businessImpact:
      "Reduce return anxiety and unlock electronics, personal care, and home essentials growth.",
  },
  {
    id: "ins-3",
    problem:
      "Competing platforms win on search breadth while Blinkit wins on speed — users don't connect the two.",
    opportunity:
      "Reframe Blinkit as 'fast everything' through occasion-based merchandising, not catalog dumps.",
    productDirection:
      "Occasion hubs ('Weekend reset', 'Work-from-home setup') bundling cross-category items.",
    businessImpact:
      "Drive new purchase occasions and improve category penetration among power users.",
  },
]

export const methodologySteps = [
  {
    title: "Collect",
    description: "Gather public conversations from Reddit, forums, and social platforms.",
    icon: "database" as const,
  },
  {
    title: "Retrieve",
    description: "Extract candidate evidence using semantic search and keyword filters.",
    icon: "search" as const,
  },
  {
    title: "Classify",
    description: "Tag signals by behavioral theme, barrier type, and JTBD framework.",
    icon: "tags" as const,
  },
  {
    title: "Human Validation",
    description: "Research team reviews and scores each signal for relevance and confidence.",
    icon: "check-circle" as const,
  },
  {
    title: "Synthesize",
    description: "Cluster validated signals into actionable insights and product directions.",
    icon: "lightbulb" as const,
  },
]

export const filterOptions = {
  platforms: ["All Platforms", "Reddit", "Twitter/X", "Forums"],
  barriers: ["All Barriers", "Unaware of assortment", "Habitual grocery framing", "Insufficient product context"],
  themes: ["All Themes", "Category Awareness", "Mental Availability", "Decision Confidence"],
  categories: ["All Categories", "Electronics", "Personal Care", "Home & Living", "Snacks & Beverages"],
}
