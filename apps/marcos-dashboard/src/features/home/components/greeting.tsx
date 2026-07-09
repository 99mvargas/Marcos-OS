import { formatFullDate, greetingForHour } from "@/lib/format"

export function Greeting({ name }: { name: string }) {
  return (
    <div className="space-y-0.5">
      <p className="text-sm font-medium text-muted-foreground">{formatFullDate()}</p>
      <h1 className="text-[26px] font-semibold tracking-tight text-foreground">
        {greetingForHour()}, {name}
      </h1>
    </div>
  )
}
