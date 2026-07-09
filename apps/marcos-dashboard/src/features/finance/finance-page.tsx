import { Wallet, Landmark, CreditCard, TrendingUp, CalendarClock } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardAction } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatCurrency } from "@/lib/format"
import { MOCK_FINANCIAL_SNAPSHOT } from "@/data/mock/finance"

type SummaryCardDef = {
  id: string
  label: string
  icon: LucideIcon
  value: string
}

const snapshot = MOCK_FINANCIAL_SNAPSHOT

const SUMMARY_CARDS: SummaryCardDef[] = [
  { id: "net-worth", label: "Net Worth", icon: Wallet, value: formatCurrency(snapshot.netWorth) },
  { id: "cash", label: "Cash", icon: Landmark, value: formatCurrency(snapshot.cash) },
  {
    id: "total-debt",
    label: "Total Debt",
    icon: CreditCard,
    value: formatCurrency(snapshot.totalDebt),
  },
  {
    id: "investments",
    label: "Investments",
    icon: TrendingUp,
    value: formatCurrency(snapshot.investments),
  },
  {
    id: "debt-free-date",
    label: "Debt-Free Date",
    icon: CalendarClock,
    value: snapshot.projectedDebtFreeDate ?? "Not yet projected",
  },
]

export function FinancePage() {
  return (
    <div>
      <h2 className="mb-2.5 text-[15px] font-semibold tracking-tight">Finance</h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {SUMMARY_CARDS.map((card) => (
          <Card key={card.id}>
            <CardHeader>
              <div className="flex items-center gap-2">
                <card.icon className="size-4 text-muted-foreground" strokeWidth={2} />
                <CardTitle>{card.label}</CardTitle>
              </div>
              <CardAction>
                <Badge variant="secondary">Demo Data</Badge>
              </CardAction>
            </CardHeader>
            <CardContent>
              <p className="text-lg font-semibold text-foreground">{card.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
