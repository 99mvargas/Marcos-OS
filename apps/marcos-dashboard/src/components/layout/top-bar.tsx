import { Moon, Sun } from "lucide-react"
import { useTheme } from "@/hooks/use-theme"
import { Button } from "@/components/ui/button"

export function TopBar() {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="pt-safe sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-lg items-center justify-between px-5 py-3.5">
        <div className="flex items-center gap-2.5">
          <div className="flex size-7 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-indigo-700 text-[13px] font-bold text-white shadow-sm shadow-violet-900/20">
            M
          </div>
          <span className="text-[15px] font-semibold tracking-tight">Marcos OS</span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="size-9 rounded-full text-muted-foreground hover:text-foreground"
          onClick={toggleTheme}
          aria-label="Toggle dark mode"
        >
          {theme === "dark" ? <Sun className="size-4.5" /> : <Moon className="size-4.5" />}
        </Button>
      </div>
    </header>
  )
}
