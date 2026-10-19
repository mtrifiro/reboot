import { useEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";

/** Long text cut to a few lines, with "More" only when there is more:
 *  an ordinary short entry gets no control at all. Measured while
 *  clamped, and watched, since the text arrives after the first paint
 *  and a narrower window turns two lines into three. */
export function Clamp({ lines = 4, children }: { lines?: number; children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [overflows, setOverflows] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el || open) return;
    const measure = () => setOverflows(el.scrollHeight - el.clientHeight > 2);
    measure();
    const watch = new ResizeObserver(measure);
    watch.observe(el);
    return () => watch.disconnect();
  }, [open, children]);
  return (
    <>
      <div
        ref={ref}
        className={open ? undefined : "clamped"}
        style={open ? undefined : ({ "--clamp-lines": lines } as CSSProperties)}
      >
        {children}
      </div>
      {(overflows || open) && (
        <button className="clamp-more" type="button" aria-expanded={open} onClick={() => setOpen((v) => !v)}>
          {open ? "Less" : "More"}
        </button>
      )}
    </>
  );
}
