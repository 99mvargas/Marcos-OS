import { Wallet, Building2 } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { MOCK_HIGHEST_ROI_TODAY } from "@/data/mock/highest-roi"
import type { HighestRoiItem } from "@/data/mock/highest-roi"

const ICONS: Record<HighestRoiItem["icon"], LucideIcon> = {
  finance: Wallet,
  infrastructure: Building2,
}

export function HighestRoiToday() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Highest ROI Today</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {MOCK_HIGHEST_ROI_TODAY.map((item, index) => {
          const Icon = ICONS[item.icon]
          return (
            <div key={item.id}>
              {index > 0 && <Separator className="mb-4" />}
              <div className="flex items-start gap-3">
                <div className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg bg-accent">
                  <Icon className="size-4.5 text-accent-foreground" strokeWidth={2} />
                </div>
                <div className="min-w-0 flex-1 space-y-0.5">
                  <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    {item.executive}
                  </p>
                  <p className="text-sm font-semibold text-foreground">{item.headline}</p>
                  <p className="text-sm text-muted-foreground">{item.detail}</p>
                </div>
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
