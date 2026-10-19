import { useId, useState, type ReactNode } from "react";

/** A small ⓘ that explains the thing beside it, on hover and on
 *  focus: a button, so the keyboard reaches it, tied to its tip by
 *  `aria-describedby`, so a screen reader reads it. Never `title=`
 *  alone, which neither the keyboard nor a touch screen can open. */
export function InfoTip({ children }: { children: ReactNode }) {
  const id = useId();
  return (
    <span className="tip-wrap">
      <button
        type="button"
        className="info-mark"
        aria-describedby={id}
        aria-label="What this means"
        onClick={(e) => e.preventDefault()}
      >
        i
      </button>
      <span role="tooltip" id={id} className="tip">
        {children}
      </span>
    </span>
  );
}

/** A control that explains itself. A click puts the tip away, since the
 *  user has decided; it comes back when the pointer or the focus does. */
export function TipWrap({ tip, children }: { tip: ReactNode; children: ReactNode }) {
  const id = useId();
  const [quiet, setQuiet] = useState(false);
  return (
    <span
      className={quiet ? "tip-wrap quiet" : "tip-wrap"}
      aria-describedby={id}
      onClickCapture={() => setQuiet(true)}
      onPointerLeave={() => setQuiet(false)}
      onBlur={() => setQuiet(false)}
    >
      {children}
      <span role="tooltip" id={id} className="tip">
        {tip}
      </span>
    </span>
  );
}
