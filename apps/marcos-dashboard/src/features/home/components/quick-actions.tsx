import { useNavigate } from "react-router-dom"
import { motion } from "motion/react"
import { Lightbulb, Bot, Map, ListPlus } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import type { QuickAction } from "@/types/dashboard"

const ACTIONS: (Omit<QuickAction, "icon"> & { icon: LucideIcon; to?: string })[] = [
  { id: "q1", label: "Capture Idea", icon: Lightbulb, to: "/capture" },
  { id: "q2", label: "Ask AI", icon: Bot, to: "/ai" },
  { id: "q3", label: "Roadmap", icon: Map },
  { id: "q4", label: "New Task", icon: ListPlus },
]

export function QuickActions() {
  const navigate = useNavigate()

  return (
    <div>
      <h2 className="mb-2.5 text-[15px] font-semibold tracking-tight">Quick Actions</h2>
      <div className="grid grid-cols-4 gap-2.5">
        {ACTIONS.map((action) => (
          <motion.button
            key={action.id}
            whileTap={{ scale: 0.93 }}
            onClick={() => action.to && navigate(action.to)}
            className="flex flex-col items-center gap-1.5 rounded-xl bg-card p-3 text-center ring-1 ring-foreground/10 transition-colors active:bg-accent"
          >
            <span className="flex size-9 items-center justify-center rounded-full bg-accent">
              <action.icon className="size-4 text-accent-foreground" strokeWidth={2} />
            </span>
            <span className="text-[11px] font-medium leading-tight text-foreground">
              {action.label}
            </span>
          </motion.button>
        ))}
      </div>
    </div>
  )
}
