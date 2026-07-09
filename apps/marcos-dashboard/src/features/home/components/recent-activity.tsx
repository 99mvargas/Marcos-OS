import { FlagTriangleRight, FileText, Sparkles, GitCommitHorizontal, Scale } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { formatRelativeTime } from "@/lib/format"
import type { ActivityItem, ActivityKind } from "@/types/dashboard"

const KIND_ICON: Record<ActivityKind, LucideIcon> = {
  sprint: FlagTriangleRight,
  spec: FileText,
  capture: Sparkles,
  commit: GitCommitHorizontal,
  decision: Scale,
}

export function RecentActivity({ items }: { items: ActivityItem[] }) {
  return (
    <div>
      <h2 className="mb-2.5 text-[15px] font-semibold tracking-tight">Recent Activity</h2>
      <ul className="space-y-0">
        {items.map((item, index) => {
          const Icon = KIND_ICON[item.kind]
          const isLast = index === items.length - 1
          return (
            <li key={item.id} className="flex gap-3">
              <div className="flex flex-col items-center">
                <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-accent ring-4 ring-background">
                  <Icon className="size-3.5 text-accent-foreground" strokeWidth={2} />
                </span>
                {!isLast && <span className="w-px flex-1 bg-border" />}
              </div>
              <div className={`min-w-0 flex-1 ${isLast ? "pb-0" : "pb-4"}`}>
                <p className="text-sm font-medium text-foreground">{item.title}</p>
                <p className="text-xs text-muted-foreground">{item.detail}</p>
                <p className="mt-0.5 text-[11px] text-muted-foreground/70">
                  {formatRelativeTime(item.timestamp)}
                </p>
              </div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
