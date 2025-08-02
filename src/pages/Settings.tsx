import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useThemeContext } from "@/hooks/use-theme"


export function Settings() {
  const { theme, setTheme } = useThemeContext()

  return (
    <div className="mx-auto grid w-full max-w-6xl gap-2">
      <h1 className="text-3xl font-semibold">Settings</h1>
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Profile</CardTitle>
              <CardDescription>
                This is how others will see you on the site.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form className="grid gap-4">
                <Input placeholder="Name" defaultValue="Test User" />
                <Input placeholder="Email" defaultValue="test@example.com" />
              </form>
            </CardContent>
            <CardFooter className="border-t px-6 py-4">
              <Button>Save</Button>
            </CardFooter>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Theme</CardTitle>
              <CardDescription>
                Choose your preferred theme for the application.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form>
                <Select value={theme} onValueChange={(value) => setTheme(value as 'light' | 'dark' | 'system')}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select theme" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="dark">Dark</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                  </SelectContent>
                </Select>
              </form>
            </CardContent>
             <CardFooter className="border-t px-6 py-4">
              <Button>Save</Button>
            </CardFooter>
          </Card>
        </div>
    </div>
  )
}

export default Settings
