import type { ReactNode } from "react";

/** One of eight colours that stays with a thing everywhere: picked from
 *  a stable key (its id, never its name, so a rename keeps it). `hue`
 *  gives 1..8, for `avatar-<n>` or `cat-<n>`; `Tag` shows a category
 *  (a room type, a tag, a team) in its colour. */
export function hue(id: string): number {
  let h = 0;
  for (const ch of id) h = (h * 31 + ch.charCodeAt(0)) % 8;
  return h + 1;
}

export function Tag({ id, children }: { id: string; children: ReactNode }) {
  return <span className={`tag cat-${hue(id)}`}>{children}</span>;
}
