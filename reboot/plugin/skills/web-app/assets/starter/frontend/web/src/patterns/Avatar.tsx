import { hue } from "./Hue";

/** A person as their initials, in a colour that is theirs everywhere:
 *  one of the eight `--avatar-*` tokens, picked from a stable key (their
 *  id, not their name, so a rename keeps the colour). Decorative beside
 *  the name it goes with; alone, it carries the name as its label. */
export function Avatar({
  name,
  id,
  size = 28,
  alone = false,
}: {
  name: string;
  id: string;
  size?: number;
  alone?: boolean;
}) {
  const initials = name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0]!.toUpperCase())
    .join("");
  return (
    <span
      className={`avatar avatar-${hue(id)}`}
      style={{ width: size, height: size, fontSize: Math.round(size * 0.4) }}
      {...(alone ? { role: "img", "aria-label": name } : { "aria-hidden": true })}
    >
      {initials || "?"}
    </span>
  );
}
