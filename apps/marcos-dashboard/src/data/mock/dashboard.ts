import type { DashboardSnapshot } from "@/types/dashboard"

export const MOCK_DASHBOARD_SNAPSHOT: DashboardSnapshot = {
  ownerName: "Marcos",
  currentSprint: {
    number: 11,
    name: "Marcos OS Dashboard",
    description: "Building the primary interface for Marcos OS — a mobile-first PWA.",
    progress: 35,
    status: "In Progress",
  },
  currentTask: {
    title: "Build Home Screen — v0.1",
    detail: "Premium dashboard experience with mock data, before wiring real APIs.",
    startedAt: new Date(Date.now() - 55 * 60 * 1000).toISOString(),
    status: "Active",
  },
  focusItems: [
    { id: "f1", title: "Call Sara about the weekend", domain: "Family", done: false },
    { id: "f2", title: "Approve the PostgreSQL migration plan", domain: "Business", done: false },
    { id: "f3", title: "Review outstanding invoices", domain: "Finance", done: false },
    { id: "f4", title: "20-minute walk before lunch", domain: "Health", done: true },
  ],
  builderStatus: {
    state: "Active",
    agent: "Claude Code",
    lastAction: "Building Home screen (Dashboard v0.1)",
    lastActionAt: new Date(Date.now() - 4 * 60 * 1000).toISOString(),
    branch: "main",
  },
  activity: [
    {
      id: "a1",
      kind: "decision",
      title: "Engineering Operating Manual approved",
      detail: "Team roles, lifecycle, and session protocol locked in.",
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: "a2",
      kind: "spec",
      title: "PROJECT_STATE.md specification written",
      detail: "Repository Status and Session Objective sections added.",
      timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: "a3",
      kind: "spec",
      title: "Memory Architecture v1 revised",
      detail: "Constitution, Semantic Memory Layer seam added.",
      timestamp: new Date(Date.now() - 26 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: "a4",
      kind: "commit",
      title: "Sprint 010: Chief of Staff Engine merged",
      detail: "Curation pipeline now selects the daily recommendation set.",
      timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: "a5",
      kind: "capture",
      title: "New capture: Knowledge Capture System",
      detail: "Proposal drafted for cross-model knowledge retention.",
      timestamp: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ],
}
