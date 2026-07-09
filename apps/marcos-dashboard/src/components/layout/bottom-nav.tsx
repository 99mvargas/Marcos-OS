import { NavLink } from "react-router-dom"
import { motion } from "motion/react"
import { Home, Lightbulb, Bot, Settings } from "lucide-react"
import { cn } from "@/lib/utils"

const NAV_ITEMS = [
  { to: "/", label: "Home", icon: Home, end: true },
  { to: "/capture", label: "Capture", icon: Lightbulb, end: false },
  { to: "/ai", label: "AI", icon: Bot, end: false },
  { to: "/system", label: "System", icon: Settings, end: false },
] as const

export function BottomNav() {
  return (
    <nav
      className="pb-safe fixed inset-x-0 bottom-0 z-50 border-t border-border/60 bg-background/80 backdrop-blur-xl"
      aria-label="Primary"
    >
      <ul className="mx-auto flex max-w-lg items-stretch justify-around px-2">
        {NAV_ITEMS.map((item) => (
          <li key={item.to} className="flex-1">
            <NavLink
              to={item.to}
              end={item.end}
              className="relative flex flex-col items-center gap-1 px-2 py-2.5 text-xs font-medium text-muted-foreground transition-colors"
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.span
                      layoutId="bottom-nav-active"
                      className="absolute inset-x-2 top-0 h-0.5 rounded-full bg-primary"
                      transition={{ type: "spring", stiffness: 500, damping: 35 }}
                    />
                  )}
                  <item.icon
                    className={cn(
                      "size-5 transition-all",
                      isActive ? "scale-105 text-primary" : "text-muted-foreground",
                    )}
                    strokeWidth={isActive ? 2.3 : 2}
                  />
                  <span className={cn(isActive ? "text-foreground" : "text-muted-foreground")}>
                    {item.label}
                  </span>
                </>
              )}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}
