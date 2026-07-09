import { motion } from "motion/react"
import type { LucideIcon } from "lucide-react"

type ComingSoonProps = {
  icon: LucideIcon
  title: string
  description: string
}

export function ComingSoon({ icon: Icon, title, description }: ComingSoonProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="flex min-h-[70svh] flex-col items-center justify-center gap-4 text-center"
    >
      <div className="flex size-16 items-center justify-center rounded-2xl bg-accent">
        <Icon className="size-7 text-accent-foreground" strokeWidth={1.75} />
      </div>
      <div className="space-y-1.5">
        <h1 className="text-lg font-semibold tracking-tight">{title}</h1>
        <p className="mx-auto max-w-[26ch] text-sm text-muted-foreground">{description}</p>
      </div>
    </motion.div>
  )
}
