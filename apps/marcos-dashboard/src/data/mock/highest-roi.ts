export type HighestRoiItem = {
  id: string
  executive: string
  icon: "finance" | "infrastructure"
  headline: string
  detail: string
}

export const MOCK_HIGHEST_ROI_TODAY: HighestRoiItem[] = [
  {
    id: "finance-pay-down-debt",
    executive: "Finance Executive",
    icon: "finance",
    headline: "Pay $250 toward your highest-interest credit card.",
    detail: "Estimated debt-free improvement: +5 days",
  },
  {
    id: "infra-status",
    executive: "Infrastructure Executive",
    icon: "infrastructure",
    headline: "Builder VM healthy.",
    detail: "All core services online.",
  },
]
