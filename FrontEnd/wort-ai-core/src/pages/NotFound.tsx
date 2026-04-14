import { Link, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { ROUTES } from "@/lib/routes";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted">
      <div className="text-center">
        <h1 className="mb-4 text-4xl font-bold">404</h1>
        <p className="mb-4 text-xl text-muted-foreground">Oops! Page not found</p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center text-base">
          <Link to={ROUTES.home} className="text-primary underline hover:text-primary/90">
            Return to Home
          </Link>
          <span className="hidden sm:inline text-muted-foreground">·</span>
          <Link to={ROUTES.about} className="text-primary underline hover:text-primary/90">
            About
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
