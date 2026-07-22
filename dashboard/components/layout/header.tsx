"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { motion } from "framer-motion"
import { GitHubIcon } from "@/components/ui/github-icon"
import { Button } from "@/components/ui/button"
import { navLinks } from "@/lib/data"
import { cn } from "@/lib/utils"

export function Header() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener("scroll", onScroll, { passive: true })
    return () => window.removeEventListener("scroll", onScroll)
  }, [])

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className={cn(
        "sticky top-0 z-50 w-full transition-all duration-300",
        scrolled
          ? "border-b border-border/80 bg-[#F8F8F5]/90 shadow-sm backdrop-blur-xl"
          : "bg-transparent"
      )}
    >
      <div className="mx-auto flex h-16 max-w-[1400px] items-center justify-between px-6 lg:px-8">
        <Link href="#overview" className="group flex items-center gap-2.5">
          <span className="flex size-7 items-center justify-center rounded-full bg-blinkit-green shadow-sm">
            <span className="size-2.5 rounded-full bg-white/90" />
          </span>
          <span className="hidden text-sm font-semibold tracking-tight text-foreground sm:inline">
            Blinkit Category Discovery Engine
          </span>
          <span className="text-sm font-semibold tracking-tight text-foreground sm:hidden">
            Blinkit CDE
          </span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-xl px-3.5 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-white hover:text-foreground"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Button
            variant="outline"
            size="sm"
            className="h-9 gap-2 rounded-xl border-border bg-white px-4 shadow-sm hover:bg-white hover:shadow-md"
            render={<a href="https://github.com" target="_blank" rel="noopener noreferrer" />}
          >
            <GitHubIcon />
            <span className="hidden sm:inline">GitHub</span>
          </Button>
        </motion.div>
      </div>
    </motion.header>
  )
}
