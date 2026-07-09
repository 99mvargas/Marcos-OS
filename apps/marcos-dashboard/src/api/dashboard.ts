import type { DashboardSnapshot } from "@/types/dashboard"
import { MOCK_DASHBOARD_SNAPSHOT } from "@/data/mock/dashboard"

const SIMULATED_LATENCY_MS = 420

/**
 * Returns the current dashboard snapshot.
 *
 * v0.1 returns mock data with a simulated network delay so loading states
 * are real, not skipped. When marcos-core exposes a REST API, only this
 * function's body changes — no caller is affected.
 */
export async function getDashboardSnapshot(): Promise<DashboardSnapshot> {
  await new Promise((resolve) => setTimeout(resolve, SIMULATED_LATENCY_MS))
  return MOCK_DASHBOARD_SNAPSHOT
}
