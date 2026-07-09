import { useNavigate } from "react-router-dom"
import { motion } from "motion/react"
import { Home, Wallet, Building2, Brain, Briefcase, ShoppingCart, Heart } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

type ExecutiveItem = {
  id: string
  label: string
  icon: LucideIcon
  to?: string
  comingSoon?: boolean
}

const EXECUTIVES: ExecutiveItem[] = [
  { id: "home", label: "Home", icon: Home, to: "/" },
  { id: "finance", label: "Finance Executive", icon: Wallet, to: "/finance" },
  { id: "infrastructure", label: "Infrastructure Executive", icon: Building2, to: "/" },
  { id: "knowledge", label: "Knowledge Executive", icon: Brain, comingSoon: true },
  { id: "business", label: "Business Executive", icon: Briefcase, comingSoon: true },
  { id: "purchasing", label: "Purchasing Executive", icon: ShoppingCart, comingSoon: true },
  { id: "health", label: "Health Executive", icon: Heart, comingSoon: true },
]

export function ExecutivesNav() {
  const navigate = useNavigate()

  return (
    <div>
      <h2 className="mb-2.5 text-[15px] font-semibold tracking-tight">Executives</h2>
      <div className="grid grid-cols-4 gap-2.5">
        {EXECUTIVES.map((executive) => (
          <motion.button
            key={executive.id}
            type="button"
            disabled={executive.comingSoon}
            aria-disabled={executive.comingSoon}
            whileTap={executive.comingSoon ? undefined : { scale: 0.93 }}
            onClick={() => executive.to && navigate(executive.to)}
            className={cn(
              "flex flex-col items-center gap-1.5 rounded-xl bg-card p-3 text-center ring-1 ring-foreground/10 transition-colors",
              executive.comingSoon
                ? "cursor-not-allowed opacity-50"
                : "active:bg-accent"
            )}
          >
            <span className="flex size-9 items-center justify-center rounded-full bg-accent">
              <executive.icon className="size-4 text-accent-foreground" strokeWidth={2} />
            </span>
            <span className="text-[11px] font-medium leading-tight text-foreground">
              {executive.label}
            </span>
          </motion.button>
        ))}
      </div>
    </div>
  )
}
