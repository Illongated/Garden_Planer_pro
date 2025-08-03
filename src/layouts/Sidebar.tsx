import { NavLink } from 'react-router-dom'
import { Bell, Home, Package, Package2, Settings, Users, Sun, Moon, LayoutGrid, GitBranch } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useThemeContext } from '@/hooks/use-theme'
import { cn } from '@/lib/utils'

const Sidebar = () => {
  const { theme, setTheme } = useThemeContext();

  const navLinkClasses = ({ isActive }: { isActive: boolean }) =>
    cn(
      "flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary",
      { "text-primary bg-muted": isActive }
    );

  return (
    <div className="hidden border-r bg-muted/40 md:block">
      <div className="flex h-full max-h-screen flex-col gap-2">
        <div className="flex h-14 items-center border-b px-4 lg:h-[60px] lg:px-6">
          <NavLink to="/" className="flex items-center gap-2 font-semibold">
            <Package2 className="h-6 w-6" />
            <span className="">Agrotique</span>
          </NavLink>
          <Button variant="outline" size="icon" className="ml-auto h-8 w-8">
            <Bell className="h-4 w-4" />
            <span className="sr-only">Toggle notifications</span>
          </Button>
        </div>
        <div className="flex-1">
          <nav className="grid items-start px-2 text-sm font-medium lg:px-4">
            <NavLink to="/dashboard" className={navLinkClasses}>
              <Home className="h-4 w-4" />
              Dashboard
            </NavLink>
            <NavLink to="/planner" className={navLinkClasses}>
              <LayoutGrid className="h-4 w-4" />
              Planner
            </NavLink>
            <NavLink to="/gardens" className={navLinkClasses}>
              <Package className="h-4 w-4" />
              Gardens
            </NavLink>
            <NavLink to="/projects" className={navLinkClasses}>
              <GitBranch className="h-4 w-4" />
              Projects
            </NavLink>
            <NavLink to="/settings" className={navLinkClasses}>
              <Settings className="h-4 w-4" />
              Settings
            </NavLink>
          </nav>
        </div>
        <div className="mt-auto p-4">
          <Card>
            <CardHeader className="p-2 pt-0 md:p-4">
              <CardTitle>Upgrade to Pro</CardTitle>
              <CardDescription>
                Unlock all features and get unlimited access to our support
                team.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-2 pt-0 md:p-4 md:pt-0">
              <Button size="sm" className="w-full">
                Upgrade
              </Button>
            </CardContent>
          </Card>
        </div>
        <div className="flex items-center justify-center p-4">
            <Button variant="ghost" size="icon" onClick={() => setTheme('light')}>
                <Sun className={`h-5 w-5 ${theme === 'light' ? '' : 'text-muted-foreground'}`}/>
            </Button>
            <Button variant="ghost" size="icon" onClick={() => setTheme('dark')}>
                <Moon className={`h-5 w-5 ${theme === 'dark' ? '' : 'text-muted-foreground'}`}/>
            </Button>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
