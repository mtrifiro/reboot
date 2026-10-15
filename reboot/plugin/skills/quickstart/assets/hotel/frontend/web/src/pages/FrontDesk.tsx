import { useHotel } from "@api/hotel/v1/hotel_rbt_react";
import { useReservation } from "@api/reservations/v1/reservations_rbt_react";
import { useEffect, useMemo, useState } from "react";
import { HOTEL_ID } from "../App";
import { friendlyError } from "../errors";
import { can, type Role } from "../rooms";

type Aborted = {
  error: { type: string } & Record<string, unknown>;
  message: string;
};

function isoDay(d: Date): string {
  const p = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

function addDays(iso: string, n: number): string {
  const [y, m, d] = iso.split("-").map(Number);
  return isoDay(new Date(y, m - 1, d + n));
}

function nightsBetween(a: string, b: string): number {
  return Math.round(
    (new Date(`${b}T00:00:00`).getTime() - new Date(`${a}T00:00:00`).getTime()) /
      86400000,
  );
}

// The wall clock at the hotel, as "YYYY-MM-DD HH:MM", whatever the
// time zone of the computer showing the page.
function hotelNow(timeZone: string): string {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(new Date());
  const get = (t: string) => parts.find((p) => p.type === t)?.value ?? "";
  return `${get("year")}-${get("month")}-${get("day")} ${get("hour")}:${get("minute")}`;
}

function checkInOpen(
  arrival: string,
  checkInTime: string,
  timeZone: string,
  _tick: number,
): boolean {
  if (!timeZone || !checkInTime) return true;
  return hotelNow(timeZone) >= `${arrival} ${checkInTime}`;
}

function shortDay(iso: string): { dow: string; dm: string } {
  const d = new Date(`${iso}T00:00:00`);
  return {
    dow: d.toLocaleDateString(undefined, { weekday: "short" }),
    dm: d.toLocaleDateString(undefined, { day: "numeric", month: "short" }),
  };
}

export default function FrontDeskPage({ role }: { role: Role }) {
  const today = isoDay(new Date());
  const [day, setDay] = useState(today);
  const hotel = useHotel({ id: HOTEL_ID });
  const { response, aborted } = hotel.useFrontDesk({ date: day });
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [chosen, setChosen] = useState<Record<string, string>>({});
  // Re-render each minute, so arrivals stop showing as early at 3 pm.
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const id = window.setInterval(() => setTick((t) => t + 1), 60000);
    return () => window.clearInterval(id);
  }, []);

  const [guest, setGuest] = useState("");
  const [roomType, setRoomType] = useState("Deluxe King");
  const [arrival, setArrival] = useState(today);
  const [departure, setDeparture] = useState(addDays(today, 2));

  const desk = can.frontDesk(role);

  const act = async (
    label: string,
    call: () => Promise<{ aborted?: Aborted }>,
  ) => {
    setBusy(true);
    setError(null);
    setDone(null);
    const { aborted } = await call();
    setBusy(false);
    if (aborted !== undefined) setError(friendlyError(aborted));
    else setDone(label);
    return aborted === undefined;
  };

  const readyByType = useMemo(() => {
    const m: Record<string, string[]> = {};
    for (const r of response?.readyRooms ?? []) {
      (m[r.roomType] ??= []).push(r.number);
    }
    for (const numbers of Object.values(m)) {
      numbers.sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
    }
    return m;
  }, [response]);

  const arrivals = response?.arrivals ?? [];
  const departures = response?.departures ?? [];
  const pending = arrivals.filter((a) => a.status === "booked").length;
  const isToday = day === today;

  return (
    <>
      <section className="brand-band">
        <div className="page-head">
          <div>
            <p className="eyebrow">Front desk</p>
            <h1>{isToday ? "Today" : shortDay(day).dow + " " + shortDay(day).dm}</h1>
            <p className="lede">
              Who is arriving and leaving, which rooms are ready to give out,
              and what's left to sell over the next two weeks.
            </p>
          </div>
          <div className="actions day-picker">
            <label htmlFor="day">Day</label>
            <input
              id="day"
              type="date"
              value={day}
              onChange={(e) => e.target.value && setDay(e.target.value)}
            />
            {!isToday && (
              <button onClick={() => setDay(today)}>Back to today</button>
            )}
          </div>
        </div>
      </section>
      <main>
        <div className="stats">
          <div className="stat">
            <div className="label">Still to arrive</div>
            <div className="value">{response ? pending : "–"}</div>
            <div className="small muted">
              of {arrivals.length} arriving
            </div>
          </div>
          <div className="stat">
            <div className="label">Due to leave</div>
            <div className="value">{response ? departures.length : "–"}</div>
          </div>
          <div className="stat">
            <div className="label">In house</div>
            <div className="value">{response?.inHouse ?? "–"}</div>
          </div>
          <div className="stat">
            <div className="label">Ready to give out</div>
            <div className="value">{response?.readyRooms.length ?? "–"}</div>
          </div>
        </div>

        {(error || done) && (
          <div
            className={`notice toast${error ? " bad" : ""}`}
            role={error ? "alert" : "status"}
          >
            <span>{error ?? done}</span>
            <button
              className="ghost"
              onClick={() => {
                setError(null);
                setDone(null);
              }}
            >
              Dismiss
            </button>
          </div>
        )}

        {aborted !== undefined && response === undefined ? (
          <div className="error" role="alert">
            {friendlyError(aborted)}
          </div>
        ) : response === undefined ? (
          <div className="skeleton" style={{ height: 320 }} />
        ) : (
          <>
            <div className="desk-columns">
              <section className="panel">
                <div className="panel-head">
                  <h2 id="arrivals-title">Arrivals</h2>
                </div>
                {arrivals.length === 0 ? (
                  <p className="muted small">Nobody is due that day.</p>
                ) : (
                  <div className="table-wrap">
                    <table aria-labelledby="arrivals-title">
                      <thead>
                        <tr>
                          <th>Guest</th>
                          <th>Room type</th>
                          <th>Nights</th>
                          <th>Room</th>
                        </tr>
                      </thead>
                      <tbody>
                        {arrivals.map((a) => (
                          <ArrivalRow
                            key={a.reservationId}
                            arrival={a}
                            options={readyByType[a.roomType] ?? []}
                            pick={
                              chosen[a.reservationId] ??
                              readyByType[a.roomType]?.[0] ??
                              ""
                            }
                            onPick={(n) =>
                              setChosen({ ...chosen, [a.reservationId]: n })
                            }
                            role={role}
                            busy={busy}
                            early={
                              !checkInOpen(
                                a.arrival,
                                response.checkInTime,
                                response.timeZone,
                                tick,
                              )
                            }
                            checkInTime={response.checkInTime}
                            act={act}
                            checkIn={() =>
                              hotel.checkInBooking({
                                reservationId: a.reservationId,
                                roomNumber:
                                  chosen[a.reservationId] ??
                                  readyByType[a.roomType]?.[0] ??
                                  "",
                              })
                            }
                          />
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </section>

              <section className="panel">
                <div className="panel-head">
                  <h2 id="departures-title">Departures</h2>
                </div>
                {departures.length === 0 ? (
                  <p className="muted small">Nobody is due to leave.</p>
                ) : (
                  <div className="table-wrap">
                    <table aria-labelledby="departures-title">
                      <thead>
                        <tr>
                          <th>Room</th>
                          <th>Guest</th>
                          <th />
                        </tr>
                      </thead>
                      <tbody>
                        {departures.map((d) => (
                          <tr key={d.reservationId}>
                            <td className="mono">{d.roomNumber}</td>
                            <td>
                              {d.guestName}
                              {d.departure < day && (
                                <div className="small bad-text">
                                  Overdue since {d.departure}
                                </div>
                              )}
                            </td>
                            <td>
                              {desk && (
                                <button
                                  disabled={busy}
                                  aria-label={`Check out ${d.guestName}`}
                                  onClick={() =>
                                    act(
                                      `${d.guestName} checked out; room ${d.roomNumber} goes to housekeeping.`,
                                      () =>
                                        hotel.checkOutRoom({
                                          roomNumber: d.roomNumber,
                                        }),
                                    )
                                  }
                                >
                                  Check out
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </section>
            </div>

            <section className="panel">
              <div className="panel-head">
                <h2 id="availability-title">Rooms left to sell</h2>
                <span className="small muted">
                  Each night, rooms of the type not yet booked
                </span>
              </div>
              <div className="table-wrap">
                <table className="availability" aria-labelledby="availability-title">
                  <thead>
                    <tr>
                      <th>Room type</th>
                      {response.availability[0]?.nights.map((n) => {
                        const s = shortDay(n.date);
                        return (
                          <th key={n.date} className="night">
                            <span className="small muted">{s.dow}</span>
                            <br />
                            {s.dm}
                          </th>
                        );
                      })}
                    </tr>
                  </thead>
                  <tbody>
                    {response.availability.map((t) => (
                      <tr key={t.roomType}>
                        <th scope="row">
                          {t.roomType}
                          <div className="small muted">{t.totalRooms} rooms</div>
                        </th>
                        {t.nights.map((n) => (
                          <td
                            key={n.date}
                            className={`left ${n.left === 0 ? "full" : n.left / t.totalRooms <= 0.25 ? "low" : ""}`}
                            title={`${n.left} of ${t.totalRooms} left on ${n.date}`}
                          >
                            {n.left === 0 ? "Full" : n.left}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <div className="desk-columns">
              {desk && (
                <form
                  className="panel drawer-form"
                  aria-labelledby="book-title"
                  onSubmit={async (e) => {
                    e.preventDefault();
                    setBusy(true);
                    setError(null);
                    setDone(null);
                    const name = guest.trim();
                    const { response: booked, aborted } = await hotel.book({
                      guestName: guest,
                      roomType,
                      arrival,
                      departure,
                    });
                    setBusy(false);
                    if (aborted !== undefined) {
                      setError(friendlyError(aborted));
                    } else {
                      setDone(`Booked ${name}: ${booked?.reservationId}.`);
                      setGuest("");
                    }
                  }}
                >
                  <h2 id="book-title">New booking</h2>
                  <div className="field">
                    <label htmlFor="book-guest">Guest</label>
                    <input
                      id="book-guest"
                      value={guest}
                      onChange={(e) => setGuest(e.target.value)}
                    />
                  </div>
                  <div className="field">
                    <label htmlFor="book-type">Room type</label>
                    <select
                      id="book-type"
                      value={roomType}
                      onChange={(e) => setRoomType(e.target.value)}
                    >
                      {response.availability.map((t) => (
                        <option key={t.roomType} value={t.roomType}>
                          {t.roomType}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="field-row">
                    <div className="field">
                      <label htmlFor="book-arrival">Arrival</label>
                      <input
                        id="book-arrival"
                        type="date"
                        value={arrival}
                        onChange={(e) => setArrival(e.target.value)}
                      />
                    </div>
                    <div className="field">
                      <label htmlFor="book-departure">Departure</label>
                      <input
                        id="book-departure"
                        type="date"
                        value={departure}
                        onChange={(e) => setDeparture(e.target.value)}
                      />
                    </div>
                  </div>
                  <button type="submit" className="primary" disabled={busy}>
                    Book stay
                  </button>
                </form>
              )}

              <section className="panel">
                <div className="panel-head">
                  <h2 id="upcoming-title">Coming up</h2>
                  <span className="small muted">Next 14 days</span>
                </div>
                {response.upcoming.length === 0 ? (
                  <p className="muted small">No bookings in the next two weeks.</p>
                ) : (
                  <div className="table-wrap">
                    <table aria-labelledby="upcoming-title">
                      <thead>
                        <tr>
                          <th>Arrives</th>
                          <th>Guest</th>
                          <th>Room type</th>
                          <th>Nights</th>
                          <th />
                        </tr>
                      </thead>
                      <tbody>
                        {response.upcoming.map((u) => (
                          <tr key={u.reservationId}>
                            <td>{shortDay(u.arrival).dow} {shortDay(u.arrival).dm}</td>
                            <td>
                              {u.guestName}
                              <div className="mono small muted">{u.reservationId}</div>
                            </td>
                            <td>{u.roomType}</td>
                            <td>{nightsBetween(u.arrival, u.departure)}</td>
                            <td>
                              {desk && (
                                <button
                                  className="ghost"
                                  disabled={busy}
                                  aria-label={`Cancel ${u.guestName}'s booking`}
                                  onClick={() =>
                                    act(
                                      `Cancelled ${u.guestName}'s booking; the nights are free again.`,
                                      () =>
                                        hotel.cancelBooking({
                                          reservationId: u.reservationId,
                                        }),
                                    )
                                  }
                                >
                                  Cancel
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </section>
            </div>
          </>
        )}
      </main>
    </>
  );
}

type ArrivalView = {
  reservationId: string;
  guestName: string;
  roomType: string;
  arrival: string;
  departure: string;
  status: string;
  roomNumber: string;
  earlyCheckInApprovedByName: string;
};

function ArrivalRow({
  arrival: a,
  options,
  pick,
  onPick,
  role,
  busy,
  early,
  checkInTime,
  act,
  checkIn,
}: {
  arrival: ArrivalView;
  options: string[];
  pick: string;
  onPick: (room: string) => void;
  role: Role;
  busy: boolean;
  early: boolean;
  checkInTime: string;
  act: (
    label: string,
    call: () => Promise<{ aborted?: Aborted }>,
  ) => Promise<boolean>;
  checkIn: () => Promise<{ aborted?: Aborted }>;
}) {
  const reservation = useReservation({ id: a.reservationId });
  const desk = can.frontDesk(role);
  const approved = a.earlyCheckInApprovedByName;
  const booked = a.status === "booked";
  return (
    <tr>
      <td>
        {a.guestName}
        <div className="mono small muted">{a.reservationId}</div>
        {booked && approved && (
          <div className="small good-text">
            Early check-in approved by {approved}
          </div>
        )}
        {booked && early && !approved && (
          <div className="small warn-text">
            Early: check-in opens at {checkInTime}
            {can.manage(role) ? "" : ", or with a manager's approval"}
          </div>
        )}
      </td>
      <td>{a.roomType}</td>
      <td>{nightsBetween(a.arrival, a.departure)}</td>
      <td>
        {a.status === "checked_in" ? (
          <span className="pill good">In room {a.roomNumber}</span>
        ) : !desk ? (
          <span className="pill">Booked</span>
        ) : (
          <div className="inline-action">
            {options.length === 0 ? (
              <span className="small muted">No {a.roomType} inspected yet</span>
            ) : (
              <>
                <label
                  className="visually-hidden"
                  htmlFor={`room-${a.reservationId}`}
                >
                  Room for {a.guestName}
                </label>
                <select
                  id={`room-${a.reservationId}`}
                  className="inline-select"
                  value={pick}
                  onChange={(e) => onPick(e.target.value)}
                >
                  {options.map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
                <button
                  className="primary"
                  disabled={busy}
                  aria-label={`Check in ${a.guestName}`}
                  onClick={() =>
                    act(`${a.guestName} is in room ${pick}.`, checkIn)
                  }
                >
                  Check in
                </button>
              </>
            )}
            {early && !approved && can.manage(role) && (
              <button
                className="ghost"
                disabled={busy}
                aria-label={`Approve early check-in for ${a.guestName}`}
                onClick={() =>
                  act(`Early check-in approved for ${a.guestName}.`, () =>
                    reservation.approveEarlyCheckIn(),
                  )
                }
              >
                Approve early check-in
              </button>
            )}
          </div>
        )}
      </td>
    </tr>
  );
}
