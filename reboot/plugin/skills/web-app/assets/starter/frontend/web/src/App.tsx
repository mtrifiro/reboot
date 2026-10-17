import { useState, type FormEvent } from "react";
import { useSignIn, useSignOut } from "@reboot-dev/reboot-react";
import { use__Hub__, useUser } from "@api/__pkg__/v1/__pkg___rbt_react";
import type { __Thing__View } from "@api/__pkg__/v1/__pkg___rbt_types";
import { friendlyError } from "./errors";
import { ThemeToggle } from "./theme";

// The one __hub text__; its id is fixed by the backend
// (`backend/src/servicers/__hub__.py`).
const HUB_ID = "__hub__";

type Aborted = Parameters<typeof friendlyError>[0];

export default function App() {
  // `isLoading` covers the session probe; `user` is undefined when
  // signed out.
  const { user, isLoading } = useUser();
  const signIn = useSignIn();
  const signOut = useSignOut();
  const signedIn = user !== undefined;

  return (
    <>
      <header className="topbar">
        <a
          href="/"
          className="brand"
          aria-label="__APP_NAME__ home"
          onClick={(e) => {
            e.preventDefault();
            window.history.pushState(null, "", "/");
          }}
        >
          <span>__APP_NAME__</span>
        </a>
        <div className="spacer" />
        <ThemeToggle />
        {signedIn && (
          <button className="ghost" onClick={() => signOut()}>
            Sign out
          </button>
        )}
      </header>
      {isLoading ? (
        <main>
          <div className="skeleton" style={{ height: 240 }} />
        </main>
      ) : !signedIn ? (
        <main>
          <div className="empty">
            <h1>__APP_NAME__</h1>
            <p className="muted">Sign in to see the __things text__.</p>
            <div className="actions">
              <button className="primary" onClick={() => signIn()}>
                Sign in
              </button>
            </div>
          </div>
        </main>
      ) : (
        <SignedIn />
      )}
    </>
  );
}

// Mounted only once someone is signed in, so no reader is called
// without a session.
function SignedIn() {
  const hub = use__Hub__({ id: HUB_ID });
  // One reader for the whole list: the page subscribes once and
  // repaints when anyone adds a __thing text__.
  const list = hub.use__Things__();
  const [name, setName] = useState("");
  const [note, setNote] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function add(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const { aborted } = await hub.add__Thing__({ name, note });
    if (aborted !== undefined) {
      // The backend refused it; `friendlyError` says why, in words.
      setError(friendlyError(aborted as unknown as Aborted));
      return;
    }
    setError(null);
    setName("");
    setNote("");
  }

  return (
    <main>
      <div className="page-head">
        <h1 id="__things__-heading">__Things text__</h1>
      </div>
      <section className="panel">
        {/* Each field's label is paired with it, so a scenario's
            `fills "Name"` finds it; the button says what it does. */}
        <form className="field-row" onSubmit={add}>
          <div className="field">
            <label htmlFor="name">Name</label>
            <input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="note">Note</label>
            <input
              id="note"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
          </div>
          <button className="primary" type="submit">
            Add
          </button>
        </form>
        {error !== null && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
      </section>
      {list.response !== undefined ? (
        <__Things__Table rows={list.response.__thingsCamel__} />
      ) : list.aborted !== undefined ? (
        <p className="error" role="alert">
          {friendlyError(list.aborted as unknown as Aborted)}
        </p>
      ) : (
        <div className="skeleton" style={{ height: 160 }} />
      )}
    </main>
  );
}

function __Things__Table({ rows }: { rows: __Thing__View[] }) {
  if (rows.length === 0) {
    return (
      <div className="empty">
        <p className="muted">Nothing here yet. Add the first one above.</p>
      </div>
    );
  }
  return (
    <div className="table-wrap">
      {/* Named by the heading, so a scenario can look inside it. */}
      <table aria-labelledby="__things__-heading">
        <thead>
          <tr>
            <th scope="col">Name</th>
            <th scope="col">Note</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.__thingCamel__Id}>
              <td>{row.name}</td>
              <td className="muted">{row.note}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
