export type SprintSummary = {
  number: number
  name: string
  description: string
  progress: number
  status: "In Progress" | "Planning" | "Blocked"
}

export type CurrentTask = {
  title: string
  detail: string
  startedAt: string
  status: "Active" | "Idle"
}

export type FocusDomain = "Faith" | "Family" | "Business" | "Health" | "Finance" | "Home"

export type FocusItem = {
  id: string
  title: string
  domain: FocusDomain
  done: boolean
}

export type BuilderStatus = {
  state: "Active" | "Idle" | "Blocked"
  agent: string
  lastAction: string
  lastActionAt: string
  branch: string
}

export type QuickAction = {
  id: string
  label: string
  icon: "capture" | "ask" | "roadmap" | "task"
}

export type ActivityKind = "sprint" | "spec" | "capture" | "commit" | "decision"

export type ActivityItem = {
  id: string
  kind: ActivityKind
  title: string
  detail: string
  timestamp: string
}

export type DashboardSnapshot = {
  ownerName: string
  currentSprint: SprintSummary
  currentTask: CurrentTask
  focusItems: FocusItem[]
  builderStatus: BuilderStatus
  activity: ActivityItem[]
}
