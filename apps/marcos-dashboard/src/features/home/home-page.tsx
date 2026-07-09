import { motion } from "motion/react"
import { useDashboardSnapshot } from "@/hooks/use-dashboard-snapshot"
import { Greeting } from "@/features/home/components/greeting"
import { HighestRoiToday } from "@/features/home/components/highest-roi-today"
import { ActionCenter } from "@/features/home/components/action-center"
import { RecentUploads } from "@/features/home/components/recent-uploads"
import { ExecutivesNav } from "@/features/home/components/executives-nav"
import { CurrentSprintCard } from "@/features/home/components/current-sprint-card"
import { CurrentTaskCard } from "@/features/home/components/current-task-card"
import { TodaysFocus } from "@/features/home/components/todays-focus"
import { BuilderStatusCard } from "@/features/home/components/builder-status-card"
import { InfrastructureSection } from "@/features/home/components/infrastructure-section"
import { QuickActions } from "@/features/home/components/quick-actions"
import { RecentActivity } from "@/features/home/components/recent-activity"
import { HomeSkeleton } from "@/features/home/components/home-skeleton"

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.07, delayChildren: 0.05 },
  },
}

const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: "easeOut" as const } },
}

export function HomePage() {
  const { status, data } = useDashboardSnapshot()

  if (status === "loading" || !data) {
    return <HomeSkeleton />
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}>
        <Greeting name={data.ownerName} />
      </motion.div>

      <motion.div variants={item}>
        <HighestRoiToday />
      </motion.div>

      <motion.div variants={item}>
        <ActionCenter />
      </motion.div>

      <motion.div variants={item}>
        <RecentUploads />
      </motion.div>

      <motion.div variants={item}>
        <ExecutivesNav />
      </motion.div>

      <motion.div variants={item}>
        <CurrentSprintCard sprint={data.currentSprint} />
      </motion.div>

      <motion.div variants={item}>
        <CurrentTaskCard task={data.currentTask} />
      </motion.div>

      <motion.div variants={item}>
        <TodaysFocus items={data.focusItems} />
      </motion.div>

      <motion.div variants={item}>
        <BuilderStatusCard status={data.builderStatus} />
      </motion.div>

      <motion.div variants={item}>
        <InfrastructureSection />
      </motion.div>

      <motion.div variants={item}>
        <QuickActions />
      </motion.div>

      <motion.div variants={item}>
        <RecentActivity items={data.activity} />
      </motion.div>
    </motion.div>
  )
}
