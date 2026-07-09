import { Check } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { FocusDomain, FocusItem } from "@/types/dashboard"

const DOMAIN_STYLES: Record<FocusDomain, string> = {
  Faith: "bg-amber-500",
  Family: "bg-rose-500",
  Health: "bg-emerald-500",
  Business: "bg-blue-500",
  Finance: "bg-teal-500",
  Home: "bg-orange-500",
}

export function TodaysFocus({ items }: { items: FocusItem[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Today's Focus</CardTitle>
      </CardHeader>
      <CardContent className="space-y-1">
        {items.map((item) => (
          <div
            key={item.id}
            className="flex items-center gap-3 rounded-lg px-1 py-2 first:pt-0 last:pb-0"
          >
            <span
              className={cn(
                "flex size-5 shrink-0 items-center justify-center rounded-full border-2 transition-colors",
                item.done ? "border-transparent bg-primary" : "border-border bg-transparent",
              )}
            >
              {item.done && <Check className="size-3 text-primary-foreground" strokeWidth={3} />}
            </span>
            <span
              className={cn(
                "flex-1 text-sm",
                item.done ? "text-muted-foreground line-through" : "text-foreground",
              )}
            >
              {item.title}
            </span>
            <span className={cn("size-1.5 shrink-0 rounded-full", DOMAIN_STYLES[item.domain])} />
            <span className="shrink-0 text-xs text-muted-foreground">{item.domain}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
