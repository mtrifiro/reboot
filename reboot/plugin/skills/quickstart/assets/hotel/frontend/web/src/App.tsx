import { Logo } from "./Logo";
import FloorPlanPage from "./pages/FloorPlan";
import { ThemeToggle } from "./theme";

export const HOTEL_ID = "hotel";

export default function App() {
  return (
    <>
      <header className="topbar">
        <span className="brand">
          <Logo />
          Halcyon House
        </span>
        <span className="spacer" />
        <ThemeToggle />
      </header>
      <FloorPlanPage />
    </>
  );
}
