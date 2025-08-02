import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const NotFound = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center">
      <h1 className="text-9xl font-bold text-primary">404</h1>
      <p className="text-2xl md:text-3xl font-light text-muted-foreground mt-4">
        Oops! Page not found.
      </p>
      <p className="mt-2 text-muted-foreground">
        The page you are looking for does not exist or has been moved.
      </p>
      <Button asChild className="mt-6">
        <Link to="/dashboard">Go to Dashboard</Link>
      </Button>
    </div>
  );
};

export default NotFound;
