import { useTeam } from "@api/staff/v1/staff_rbt_react";
import { useState } from "react";
import { TEAM_ID } from "../App";
import { friendlyError } from "../errors";
import { ROLE_LABEL, can, type Role } from "../rooms";

const ROLES: Role[] = ["manager", "front_desk", "housekeeping", ""];

export default function StaffPage({ role }: { role: Role }) {
  const team = useTeam({ id: TEAM_ID });
  const { response, aborted } = team.useMembers();
  const [email, setEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<Role>("housekeeping");
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<string | null>(null);
  const manager = can.manage(role);

  const setRole = async (userId: string, name: string, next: Role) => {
    setError(null);
    setDone(null);
    const { aborted } = await team.setRole({ userId, role: next });
    if (aborted !== undefined) setError(friendlyError(aborted));
    else setDone(`${name} is now ${ROLE_LABEL[next].toLowerCase()}.`);
  };

  const invite = async () => {
    setError(null);
    setDone(null);
    const address = email.trim();
    if (!address) {
      setError("Enter the work address to invite.");
      return;
    }
    const { aborted } = await team.invite({ email: address, role: inviteRole });
    if (aborted !== undefined) setError(friendlyError(aborted));
    else {
      setDone(`Invited ${address} as ${ROLE_LABEL[inviteRole].toLowerCase()}.`);
      setEmail("");
    }
  };

  return (
    <main>
      <div className="page-head">
        <div>
          <p className="eyebrow">Staff</p>
          <h1>Who may do what</h1>
          <p className="lede">
            Housekeeping cleans and inspects, the front desk checks guests in
            and out, managers do both and put rooms out of order.
            {!manager && " Only a manager can change roles."}
          </p>
        </div>
      </div>

      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {done && (
        <div className="notice" role="status">
          {done}
        </div>
      )}

      {aborted !== undefined && response === undefined ? (
        <div className="error" role="alert">
          {friendlyError(aborted)}
        </div>
      ) : response === undefined ? (
        <div className="skeleton" style={{ height: 200 }} />
      ) : (
        <>
          <section className="panel">
            <div className="panel-head">
              <h2 id="staff-title">On staff</h2>
            </div>
            <div className="table-wrap">
              <table aria-labelledby="staff-title">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Address</th>
                    <th>Role</th>
                  </tr>
                </thead>
                <tbody>
                  {response.members.map((m) => (
                    <tr key={m.userId}>
                      <td>{m.name}</td>
                      <td className="muted">{m.email || "unverified"}</td>
                      <td>
                        {manager ? (
                          <>
                            <label
                              className="visually-hidden"
                              htmlFor={`role-${m.userId}`}
                            >
                              Role for {m.name}
                            </label>
                            <select
                              id={`role-${m.userId}`}
                              className="inline-select"
                              value={m.role}
                              onChange={(e) =>
                                setRole(m.userId, m.name, e.target.value as Role)
                              }
                            >
                              {ROLES.map((r) => (
                                <option key={r} value={r}>
                                  {ROLE_LABEL[r]}
                                </option>
                              ))}
                            </select>
                          </>
                        ) : (
                          <span className="pill">{ROLE_LABEL[m.role]}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {response.invitations.length > 0 && (
            <section className="panel">
              <div className="panel-head">
                <h2 id="invites-title">Invited, not signed in yet</h2>
              </div>
              <div className="table-wrap">
                <table aria-labelledby="invites-title">
                  <tbody>
                    {response.invitations.map((i) => (
                      <tr key={i.email}>
                        <td>{i.email}</td>
                        <td>
                          <span className="pill">{ROLE_LABEL[i.role]}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {manager && (
            <form
              className="panel drawer-form"
              aria-labelledby="invite-title"
              onSubmit={(e) => {
                e.preventDefault();
                invite();
              }}
            >
              <h2 id="invite-title">Invite someone</h2>
              <div className="field-row">
                <div className="field">
                  <label htmlFor="invite-email">Work address</label>
                  <input
                    id="invite-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div className="field">
                  <label htmlFor="invite-role">Role</label>
                  <select
                    id="invite-role"
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value as Role)}
                  >
                    {ROLES.filter((r) => r !== "").map((r) => (
                      <option key={r} value={r}>
                        {ROLE_LABEL[r]}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <button type="submit" className="primary">
                Send invitation
              </button>
            </form>
          )}
        </>
      )}
    </main>
  );
}
