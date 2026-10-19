import { useEffect, useState } from "react";

/** Copies one field in one click and says what happened where it
 *  happened: a tick for a moment, or the browser's refusal in words
 *  (the clipboard is denied outside a secure context). It stops the
 *  click, so the row's own click (opening its drawer) doesn't run. */
export function CopyButton({ text, what }: { text: string; what: string }) {
  const [said, setSaid] = useState("");
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    if (!said) return;
    const t = window.setTimeout(() => setSaid(""), 1200);
    return () => window.clearTimeout(t);
  }, [said]);
  if (!text) return null;
  return (
    <button
      type="button"
      className={failed ? "copy-button failed" : "copy-button"}
      aria-label={`Copy ${what}`}
      onClick={async (e) => {
        e.stopPropagation();
        try {
          await navigator.clipboard.writeText(text);
          setFailed(false);
          setSaid("Copied");
        } catch {
          setFailed(true);
          setSaid("The browser didn't allow copying here");
        }
      }}
    >
      <span aria-hidden="true">{said && !failed ? "✓" : "⧉"}</span>
      {said && (
        <span role="status" className={failed ? "copy-said" : "visually-hidden"}>
          {said}
        </span>
      )}
    </button>
  );
}
