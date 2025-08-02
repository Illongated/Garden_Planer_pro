import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Link } from "react-router-dom"

const mockGardens = [
  {
    id: 'garden-1',
    name: 'My First Garden',
    description: 'A sunny spot in the backyard.',
    contains: 'Tomatoes, Cucumbers, Bell Peppers',
  },
  {
    id: 'garden-2',
    name: 'Herb Garden',
    description: 'Windowsill herb garden.',
    contains: 'Basil, Mint, Rosemary',
  }
]

const Gardens = () => {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold md:text-2xl">Your Gardens</h1>
        <Button>Create New Garden</Button>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {mockGardens.map((garden) => (
          <Link to={`/gardens/${garden.id}`} key={garden.id} className="block hover:shadow-lg transition-shadow rounded-lg">
            <Card>
              <CardHeader>
                <CardTitle>{garden.name}</CardTitle>
                <CardDescription>
                  {garden.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p>Contains: {garden.contains}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default Gardens
