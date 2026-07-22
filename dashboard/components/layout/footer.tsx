import Link from "next/link"
import { GitHubIcon } from "@/components/ui/github-icon"

export function Footer() {
  return (
    <footer className="border-t border-border bg-white">
      <div className="mx-auto flex max-w-[1400px] flex-col gap-6 px-6 py-12 lg:px-8">
        <div className="max-w-2xl">
          <h3 className="text-sm font-semibold text-foreground">Research Disclaimer</h3>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            This platform presents synthesized findings from publicly available
            conversations. All evidence is anonymized and used for research purposes
            only. Insights represent directional hypotheses, not validated product
            decisions. Data shown is placeholder content for UI demonstration.
          </p>
        </div>

        <div className="flex flex-col items-start justify-between gap-4 border-t border-border pt-6 sm:flex-row sm:items-center">
          <div className="flex items-center gap-4">
            <Link
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <GitHubIcon />
              View on GitHub
            </Link>
          </div>
          <p className="text-sm text-muted-foreground">
            Built with{" "}
            <Link
              href="https://nextjs.org"
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-foreground transition-colors hover:text-blinkit-green"
            >
              Next.js
            </Link>
          </p>
        </div>
      </div>
    </footer>
  )
}
