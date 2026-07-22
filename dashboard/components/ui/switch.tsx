"use client"

import { cn } from "@/lib/utils"

interface SwitchProps {
  label: string
  defaultChecked?: boolean
  className?: string
}

export function Switch({ label, defaultChecked = false, className }: SwitchProps) {
  return (
    <label
      className={cn(
        "flex cursor-pointer items-center justify-between gap-3 rounded-2xl border border-border bg-white px-4 py-2.5 transition-colors hover:border-blinkit-green/30",
        className
      )}
    >
      <span className="text-sm font-medium text-foreground">{label}</span>
      <div className="relative">
        <input
          type="checkbox"
          defaultChecked={defaultChecked}
          className="peer sr-only"
        />
        <div className="h-6 w-11 rounded-full bg-border transition-colors peer-checked:bg-blinkit-green peer-focus-visible:ring-2 peer-focus-visible:ring-blinkit-green/30" />
        <div className="absolute top-0.5 left-0.5 size-5 rounded-full bg-white shadow-sm transition-transform peer-checked:translate-x-5" />
      </div>
    </label>
  )
}
