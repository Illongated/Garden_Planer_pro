import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const Gardens = () => {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold md:text-2xl">Your Gardens</h1>
        <Button>Create New Garden</Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>My First Garden</CardTitle>
          <CardDescription>
            A sunny spot in the backyard.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p>Contains: Tomatoes, Cucumbers, Bell Peppers</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Herb Garden</CardTitle>
          <CardDescription>
            Windowsill herb garden.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p>Contains: Basil, Mint, Rosemary</p>
        </CardContent>
      </Card>
    </div>
  )
}

export default Gardens
