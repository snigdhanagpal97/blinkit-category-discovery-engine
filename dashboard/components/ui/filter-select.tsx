"use client"

import { ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"

interface FilterSelectProps {
  label: string
  options: string[]
  value?: string
  className?: string
}

export function FilterSelect({
  label,
  options,
  value = options[0],
  className,
}: FilterSelectProps) {
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <label className="text-xs font-medium text-muted-foreground">{label}</label>
      <div className="relative">
        <select
          defaultValue={value}
          className="h-10 w-full cursor-pointer appearance-none rounded-2xl border border-border bg-white px-4 pr-10 text-sm text-foreground transition-colors hover:border-blinkit-green/30 focus:border-blinkit-green focus:outline-none focus:ring-2 focus:ring-blinkit-green/20"
        >
          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <ChevronDown className="pointer-events-none absolute top-1/2 right-3 size-4 -translate-y-1/2 text-muted-foreground" />
      </div>
    </div>
  )
}
