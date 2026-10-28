import { useHotel } from "@api/hotel/v1/hotel_rbt_react";
import { useRoom } from "@api/rooms/v1/rooms_rbt_react";
import { useEffect, useMemo, useState } from "react";
import { HOTEL_ID } from "../App";
import { friendlyError } from "../errors";
import {
  STATUSES,
  STATUS_LABEL,
  STATUS_SHORT,
  can,
  sinceText,
  type Role,
  type Status,
} from "../rooms";

type RoomRow = {
  number: string;
  floor: number;
  roomType: string;
  features: string[];
  status: string;
  guestName: string;
  cleanedByName: string;
  outOfOrderReason: string;
  lastChangedByName: string;
  lastChangedAt: string;
  reservationId: string;
};

export default function FloorPlanPage({ role }: { role: Role }) {
  const hotel = useHotel({ id: HOTEL_ID });
  const { response, aborted } = hotel.useFloorPlan();
  const [status, setStatus] = useState<Status | "">("");
  const [roomType, setRoomType] = useState("");
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState<string | null>(null);

  // In room-number order: 201 first, floor by floor.
  const rooms = useMemo(
    () =>
      [...((response?.rooms ?? []) as RoomRow[])].sort((a, b) =>
        a.number.localeCompare(b.number, undefined, { numeric: true }),
      ),
    [response],
  );
  const types = useMemo(
    () => [...new Set(rooms.map((r) => r.roomType))],
    [rooms],
  );
  const floors = useMemo(
    () => [...new Set(rooms.map((r) => r.floor))].sort((a, b) => a - b),
    [rooms],
  );
  const counts = useMemo(() => {
    const c: Record<string, number> = {};
    for (const r of rooms) c[r.status] = (c[r.status] ?? 0) + 1;
    return c;
  }, [rooms]);

  const q = search.trim().toLowerCase();
  const matches = (r: RoomRow) =>
    (!status || r.status === status) &&
    (!roomType || r.roomType === roomType) &&
    (!q ||
      r.number.includes(q) ||
      r.guestName.toLowerCase().includes(q));
  const narrowed = status !== "" || roomType !== "" || q !== "";
  const shown = rooms.filter(matches).length;
  const clear = () => {
    setStatus("");
    setRoomType("");
    setSearch("");
  };

  const openRoom = rooms.find((r) => r.number === open);

  return (
    <>
      <section className="brand-band">
        <div className="page-head">
          <div>
            <p className="eyebrow">{response?.hotelName ?? "Maison Desk"}</p>
            <h1>Floor plan</h1>
            <p className="lede">
              Which rooms can be sold or checked into right now, and which
              still need housekeeping. Updates live for everyone.
            </p>
          </div>
        </div>
      </section>
      <main>
        <div className="stats" role="group" aria-label="Rooms by status">
          <button
            className={`stat${status === "" ? " selected" : ""}`}
            aria-pressed={status === ""}
            onClick={() => setStatus("")}
          >
            <div className="label">All rooms</div>
            <div className="value">{rooms.length || "–"}</div>
          </button>
          {STATUSES.map((s) => (
            <button
              key={s}
              className={`stat${status === s ? " selected" : ""}`}
              aria-pressed={status === s}
              onClick={() => setStatus(status === s ? "" : s)}
            >
              <div className="label">
                <span className={`swatch st-${s}`} aria-hidden="true" />
                {STATUS_LABEL[s]}
              </div>
              <div className="value">{counts[s] ?? 0}</div>
              <div className="meter">
                <span
                  style={{
                    width: `${rooms.length ? ((counts[s] ?? 0) / rooms.length) * 100 : 0}%`,
                  }}
                />
              </div>
            </button>
          ))}
        </div>

        <div className="filter-panel">
          <div className="filters">
            <div className="field">
              <label htmlFor="search">Room or guest</label>
              <input
                id="search"
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="status">Status</label>
              <select
                id="status"
                value={status}
                onChange={(e) => setStatus(e.target.value as Status | "")}
              >
                <option value="">All statuses</option>
                {STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {STATUS_LABEL[s]}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="room-type">Room type</label>
              <select
                id="room-type"
                value={roomType}
                onChange={(e) => setRoomType(e.target.value)}
              >
                <option value="">All types</option>
                {types.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
          </div>
          {narrowed && (
            <div className="filter-summary">
              <span className="muted small">
                Showing {shown} of {rooms.length} rooms
              </span>
              <button className="ghost" onClick={clear}>
                Clear filters
              </button>
            </div>
          )}
        </div>

        {aborted !== undefined && response === undefined ? (
          <div className="error" role="alert">
            {friendlyError(aborted)}
          </div>
        ) : response === undefined ? (
          <div className="skeleton" style={{ height: 420 }} />
        ) : (
          <section className="panel floor-plan" aria-labelledby="plan-title">
            <div className="panel-head">
              <h2 id="plan-title">Rooms by floor</h2>
              <ul className="legend" aria-label="Legend">
                {STATUSES.map((s) => (
                  <li key={s}>
                    <span className={`swatch st-${s}`} aria-hidden="true" />
                    {STATUS_SHORT[s]}
                  </li>
                ))}
              </ul>
            </div>
            {floors.map((floor) => (
              <div className="floor" key={floor}>
                <div className="floor-label" aria-hidden="true">
                  <span className="small muted">Floor</span>
                  <b>{floor}</b>
                </div>
                <ul className="floor-rooms" aria-label={`Floor ${floor}`}>
                  {rooms
                    .filter((r) => r.floor === floor)
                    .map((r) => (
                      <li key={r.number}>
                        <button
                          className={`room-tile st-${r.status}${matches(r) ? "" : " dim"}${open === r.number ? " open" : ""}`}
                          aria-label={`Room ${r.number}, ${r.roomType}, ${STATUS_LABEL[r.status]}${r.guestName ? `, ${r.guestName}` : ""}`}
                          onClick={() => setOpen(r.number)}
                        >
                          <span className="room-number">{r.number}</span>
                          <span className="room-type">{r.roomType}</span>
                          <span className="room-status">
                            {STATUS_SHORT[r.status]}
                          </span>
                          {r.guestName && (
                            <span className="room-guest">{r.guestName}</span>
                          )}
                        </button>
                      </li>
                    ))}
                </ul>
              </div>
            ))}
          </section>
        )}
      </main>
      {openRoom !== undefined && (
        <RoomDrawer
          key={openRoom.number}
          room={openRoom}
          role={role}
          onClose={() => setOpen(null)}
        />
      )}
    </>
  );
}

function RoomDrawer({
  room,
  role,
  onClose,
}: {
  room: RoomRow;
  role: Role;
  onClose: () => void;
}) {
  const handle = useRoom({ id: room.number });
  const hotel = useHotel({ id: HOTEL_ID });
  const [guestName, setGuestName] = useState("");
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  type Result = {
    aborted?: {
      error: { type: string } & Record<string, unknown>;
      message: string;
    };
  };
  const act = async (label: string, call: () => Promise<Result>) => {
    setBusy(true);
    setError(null);
    setDone(null);
    const { aborted } = await call();
    setBusy(false);
    if (aborted !== undefined) {
      setError(friendlyError(aborted));
    } else {
      setDone(label);
      setGuestName("");
      setReason("");
    }
  };

  const s = room.status as Status;
  const vacant = s !== "occupied" && s !== "out_of_order";

  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} />
      <aside
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
      >
        <div className="drawer-head">
          <div>
            <p className="eyebrow small muted">{room.roomType}</p>
            <h2 id="drawer-title">Room {room.number}</h2>
            <span className={`pill st-pill st-${s}`}>{STATUS_LABEL[s]}</span>
          </div>
          <span className="spacer" />
          <button className="ghost" aria-label="Close" onClick={onClose}>
            ✕
          </button>
        </div>
        <div className="drawer-body">
          <dl className="kv">
            {room.guestName && (
              <>
                <dt>Guest</dt>
                <dd>
                  {room.guestName}
                  {room.reservationId ? (
                    <span className="muted mono small"> · {room.reservationId}</span>
                  ) : (
                    <span className="muted small"> · walk-in</span>
                  )}
                </dd>
              </>
            )}
            {room.outOfOrderReason && (
              <>
                <dt>Out of order</dt>
                <dd>{room.outOfOrderReason}</dd>
              </>
            )}
            {room.cleanedByName && (
              <>
                <dt>Cleaned by</dt>
                <dd>{room.cleanedByName}</dd>
              </>
            )}
            <dt>Last change</dt>
            <dd>
              {room.lastChangedByName}
              {room.lastChangedAt && (
                <span className="muted">
                  {" "}
                  · {sinceText(room.lastChangedAt)}
                </span>
              )}
            </dd>
            <dt>Amenities</dt>
            <dd>
              <ul className="amenities">
                {room.features.map((f) => (
                  <li key={f}>{f}</li>
                ))}
              </ul>
            </dd>
          </dl>

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

          <div className="room-actions">
            {can.clean(role) && s === "vacant_dirty" && (
              <button
                className="primary"
                disabled={busy}
                onClick={() =>
                  act("Cleaning started.", () => handle.startCleaning())
                }
              >
                Start cleaning
              </button>
            )}
            {can.clean(role) && (s === "cleaning" || s === "vacant_dirty") && (
              <button
                className={s === "cleaning" ? "primary" : undefined}
                disabled={busy}
                onClick={() =>
                  act("Marked clean. It needs a second person to inspect it.", () =>
                    handle.markClean(),
                  )
                }
              >
                Mark clean
              </button>
            )}
            {can.clean(role) && s === "vacant_clean" && (
              <button
                className="primary"
                disabled={busy}
                onClick={() =>
                  act("Inspected. The room is ready to sell.", () =>
                    handle.inspectRoom(),
                  )
                }
              >
                Inspect and approve
              </button>
            )}
            {can.frontDesk(role) && s === "occupied" && (
              <button
                className="primary"
                disabled={busy}
                onClick={() =>
                  act("Checked out. Housekeeping will see it as dirty.", () =>
                    hotel.checkOutRoom({ roomNumber: room.number }),
                  )
                }
              >
                Check out
              </button>
            )}
            {can.manage(role) && s === "out_of_order" && (
              <button
                className="primary"
                disabled={busy}
                onClick={() =>
                  act("Back in service. It goes to housekeeping first.", () =>
                    handle.returnToService(),
                  )
                }
              >
                Return to service
              </button>
            )}
          </div>

          {can.frontDesk(role) && vacant && (
            <form
              className="panel drawer-form"
              aria-labelledby="check-in-title"
              onSubmit={(e) => {
                e.preventDefault();
                act(`${guestName.trim()} is checked in.`, () =>
                  handle.checkIn({ guestName }),
                );
              }}
            >
              <h3 id="check-in-title">Check in a walk-in guest</h3>
              {!can.manage(role) && (
                <p className="small muted">
                  Before 3 pm hotel time, only a manager can check in a walk-in.
                </p>
              )}
              {s !== "inspected" && (
                <p className="small muted">
                  Only an inspected room can take a guest. Booked guests are
                  checked in from the Front desk.
                </p>
              )}
              <div className="field">
                <label htmlFor="guest-name">Guest name</label>
                <input
                  id="guest-name"
                  value={guestName}
                  onChange={(e) => setGuestName(e.target.value)}
                />
              </div>
              <button type="submit" className="primary" disabled={busy}>
                Check in
              </button>
            </form>
          )}

          {can.manage(role) && s !== "occupied" && (
            <form
              className="panel drawer-form"
              aria-labelledby="ooo-title"
              onSubmit={(e) => {
                e.preventDefault();
                act("Taken out of order.", () =>
                  handle.takeOutOfOrder({ reason }),
                );
              }}
            >
              <h3 id="ooo-title">
                {s === "out_of_order" ? "Update the reason" : "Take out of order"}
              </h3>
              <div className="field">
                <label htmlFor="ooo-reason">Reason</label>
                <input
                  id="ooo-reason"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                />
              </div>
              <button type="submit" className="danger" disabled={busy}>
                {s === "out_of_order" ? "Update reason" : "Take out of order"}
              </button>
            </form>
          )}

          {role === "" && (
            <p className="muted small">
              You can see the floor plan, but a manager has to give you a role
              before you can change a room.
            </p>
          )}
        </div>
        <div className="drawer-foot">
          <button onClick={onClose}>Done</button>
        </div>
      </aside>
    </>
  );
}
