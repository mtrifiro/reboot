import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";

// The pointer settles before the card opens, so sweeping down a list
// doesn't flash a card per row, and lingers on the way out, so it can
// cross the gap into the card (ui-design.md, "Interaction Patterns").
const OPEN_DELAY = 350;
const CLOSE_DELAY = 150;
const WIDTH = 320;
const GAP = 14;
const EDGE = 8;
// Below the pointer unless the room there is too small to be worth it.
const MIN_ROOM = 220;

type Spot = { left: number; top?: number; bottom?: number; maxHeight: number };

// Placed once, by one edge, and never moved: what doesn't fit in the
// room on that side scrolls inside the card, so a body that grows as
// its data arrives pushes nothing that was already drawn.
function atPointer(x: number, y: number): Spot {
  const below = window.innerHeight - EDGE - (y + GAP);
  const above = y - GAP - EDGE;
  const left =
    x + GAP + WIDTH <= window.innerWidth - EDGE ? x + GAP : Math.max(EDGE, x - GAP - WIDTH);
  if (below >= MIN_ROOM || below >= above) return { left, top: y + GAP, maxHeight: below };
  return { left, bottom: window.innerHeight - (y - GAP), maxHeight: above };
}

/** A preview of a record that opens when the pointer rests on its
 *  name, or the name has focus. `children` is the card's body, rendered
 *  only while it is open, so a reader inside it subscribes only then.
 *  Portalled to the body, so a list's `overflow: hidden` can't clip it. */
export function HoverCard({
  trigger,
  children,
  label,
}: {
  trigger: (props: { "aria-describedby": string | undefined }) => ReactNode;
  children: ReactNode;
  /** Names the card for a screen reader. */
  label?: string;
}) {
  const [at, setAt] = useState<Spot | null>(null);
  const anchor = useRef<HTMLSpanElement>(null);
  const card = useRef<HTMLDivElement>(null);
  const timer = useRef<number | undefined>(undefined);
  const point = useRef<{ x: number; y: number } | null>(null);
  const id = useId();

  const open = () => {
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => {
      const p = point.current;
      if (p) return setAt(atPointer(p.x, p.y));
      const box = anchor.current?.getBoundingClientRect(); // from the keyboard
      if (box) setAt(atPointer(box.left, box.bottom));
    }, OPEN_DELAY);
  };
  const close = (delay = CLOSE_DELAY) => {
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setAt(null), delay);
  };
  useEffect(() => () => window.clearTimeout(timer.current), []);
  useEffect(() => {
    if (!at) return;
    const now = () => close(0);
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && now();
    // A press anywhere but the card: what it opens shouldn't sit under a preview.
    const onPress = (e: MouseEvent) => {
      if (!card.current?.contains(e.target as Node)) now();
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("mousedown", onPress, true);
    window.addEventListener("scroll", now, true);
    window.addEventListener("dragstart", now, true);
    window.addEventListener("contextmenu", now, true);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("mousedown", onPress, true);
      window.removeEventListener("scroll", now, true);
      window.removeEventListener("dragstart", now, true);
      window.removeEventListener("contextmenu", now, true);
    };
  }, [at]);

  return (
    <span
      ref={anchor}
      className="hover-anchor"
      onMouseEnter={(e) => {
        point.current = { x: e.clientX, y: e.clientY };
        open();
      }}
      onMouseMove={(e) => {
        if (!at) point.current = { x: e.clientX, y: e.clientY };
      }}
      onMouseLeave={() => {
        point.current = null;
        close();
      }}
      onFocus={open}
      onBlur={() => close(0)}
    >
      {trigger({ "aria-describedby": at ? id : undefined })}
      {at &&
        createPortal(
          <div
            ref={card}
            id={id}
            role="tooltip"
            aria-label={label}
            className="hover-card"
            style={{ left: at.left, top: at.top, bottom: at.bottom, width: WIDTH, maxHeight: at.maxHeight }}
            onMouseEnter={() => window.clearTimeout(timer.current)}
            onMouseLeave={() => close()}
          >
            {children}
          </div>,
          document.body,
        )}
    </span>
  );
}
