import { useTeam, useUser } from "@api/staff/v1/staff_rbt_react";
import { useSignIn, useSignOut } from "@reboot-dev/reboot-react";
import { useEffect, useState } from "react";
import { Logo } from "./Logo";
import FloorPlanPage from "./pages/FloorPlan";
import FrontDeskPage from "./pages/FrontDesk";
import StaffPage from "./pages/Staff";
import { ROLE_LABEL, type Role } from "./rooms";
import { ThemeToggle } from "./theme";

export const TEAM_ID = "team";
export const HOTEL_ID = "hotel";

// Two pages need no router: the path, kept in step with history.
function usePath(): [string, (to: string) => void] {
  const [path, setPath] = useState(window.location.pathname);
  useEffect(() => {
    const onPop = () => setPath(window.location.pathname);
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  const go = (to: string) => {
    window.history.pushState(null, "", to);
    setPath(to);
  };
  return [path, go];
}

export default function App() {
  const { user, isLoading } = useUser();
  const signIn = useSignIn();

  if (isLoading) {
    return (
      <main>
        <div className="skeleton" style={{ height: 240 }} />
      </main>
    );
  }
  if (user === undefined) {
    return (
      <>
        <header className="topbar">
          <span className="brand">
            <Logo />
            Maison Desk
          </span>
        </header>
        <main>
          <div className="empty">
            <h1>Maison Desk</h1>
            <p className="muted">
              The rooms, the housekeeping and the front desk of Maison
              Vingt-Trois, live. Staff only.
            </p>
            <div className="actions">
              <button className="primary" onClick={() => signIn()}>
                Sign in
              </button>
            </div>
          </div>
        </main>
      </>
    );
  }
  return <SignedIn />;
}

function SignedIn() {
  const [path, go] = usePath();
  const signOut = useSignOut();
  const team = useTeam({ id: TEAM_ID });
  const { response: me } = team.useMyRole();
  const role = (me?.role ?? "") as Role;

  const link = (to: string, label: string) => (
    <a
      href={to}
      className={path === to ? "active" : undefined}
      aria-current={path === to ? "page" : undefined}
      onClick={(e) => {
        e.preventDefault();
        go(to);
      }}
    >
      {label}
    </a>
  );

  return (
    <>
      <header className="topbar">
        <span className="brand">
          <Logo />
          Maison Desk
        </span>
        <nav aria-label="Pages">
          {link("/", "Floor plan")}
          {link("/front-desk", "Front desk")}
          {link("/staff", "Staff")}
        </nav>
        <span className="spacer" />
        {me !== undefined && (
          <span className="small" aria-label="Signed in as">
            {me.name || "Signed in"}
            {me.member && <> · {ROLE_LABEL[role]}</>}
          </span>
        )}
        <ThemeToggle />
        <button onClick={() => signOut()}>Sign out</button>
      </header>
      {me !== undefined && !me.member ? (
        <main>
          <div className="empty">
            <h1>Not on staff yet</h1>
            <p className="muted">
              You're signed in, but this address isn't on the hotel's staff
              roster. Ask a manager to invite you.
            </p>
          </div>
        </main>
      ) : path === "/front-desk" ? (
        <FrontDeskPage role={role} />
      ) : path === "/staff" ? (
        <StaffPage role={role} />
      ) : (
        <FloorPlanPage role={role} />
      )}
    </>
  );
}
