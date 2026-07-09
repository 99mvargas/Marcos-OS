import { useEffect, useState } from "react"
import type { DashboardSnapshot } from "@/types/dashboard"
import { getDashboardSnapshot } from "@/api/dashboard"

type State =
  | { status: "loading"; data: null }
  | { status: "ready"; data: DashboardSnapshot }

export function useDashboardSnapshot() {
  const [state, setState] = useState<State>({ status: "loading", data: null })

  useEffect(() => {
    let cancelled = false
    getDashboardSnapshot().then((data) => {
      if (!cancelled) setState({ status: "ready", data })
    })
    return () => {
      cancelled = true
    }
  }, [])

  return state
}
