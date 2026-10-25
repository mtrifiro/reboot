/** The band's art: quarter circles, half circles, dots and bars on a
 *  40 px grid at the band's right, laid out from the app's name, so an
 *  app keeps its pattern and two apps don't share one. Decoration only:
 *  its five tones are the band and the accent mixed (styles.css,
 *  `.band-art`), so a palette, band, paper or dark mode recolours it,
 *  and it never means anything. Fewer, paler shapes under the band's
 *  buttons. The comp draws the same pattern (comp.py, band_art.py):
 *  change one, change both. */

const CELL = 40;
const COLS = 18;
const ROWS = 6;

function seedOf(name: string): number {
  let h = 2166136261;
  for (const ch of name) {
    h ^= ch.codePointAt(0)!;
    h = Math.imul(h, 16777619) >>> 0;
  }
  return h;
}

function random(seed: number): () => number {
  let a = seed;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const KINDS = ["q0", "q1", "q2", "q3", "h0", "h1", "h2", "h3", "dot", "circle", "square", "bar"] as const;

type Shape = { kind: (typeof KINDS)[number]; x: number; y: number; tone: number };

export function bandShapes(name: string): Shape[] {
  const next = random(seedOf(name));
  const taken = new Set<number>();
  const shapes: Shape[] = [];
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      if (taken.has(r * COLS + c) || c < 5) continue;
      const underButtons = r >= 3 && c >= 8;
      const p = (0.12 + (0.43 * (c - 5)) / 12) * (underButtons ? 0.35 : 1);
      if (next() >= p) continue;
      let kind = KINDS[Math.floor(next() * KINDS.length)]!;
      const tone = underButtons ? (next() < 0.5 ? 1 : 5) : 1 + Math.floor(next() * 5);
      if (kind === "bar") {
        if (c + 1 < COLS && !taken.has(r * COLS + c + 1)) taken.add(r * COLS + c + 1);
        else kind = "square";
      }
      taken.add(r * COLS + c);
      shapes.push({ kind, x: c * CELL, y: r * CELL, tone });
    }
  }
  return shapes;
}

function draw({ kind, x, y, tone }: Shape, key: number) {
  const s = CELL;
  const h = s / 2;
  const className = `t${tone}`;
  const d: Record<string, string> = {
    q0: `M${x} ${y}h${s}a${s} ${s} 0 0 1 -${s} ${s}z`,
    q1: `M${x + s} ${y}v${s}a${s} ${s} 0 0 1 -${s} -${s}z`,
    q2: `M${x + s} ${y + s}h-${s}a${s} ${s} 0 0 1 ${s} -${s}z`,
    q3: `M${x} ${y + s}v-${s}a${s} ${s} 0 0 1 ${s} ${s}z`,
    h0: `M${x} ${y + s}a${h} ${h} 0 0 1 ${s} 0z`,
    h1: `M${x} ${y}a${h} ${h} 0 0 0 ${s} 0z`,
    h2: `M${x} ${y}a${h} ${h} 0 0 1 0 ${s}z`,
    h3: `M${x + s} ${y}a${h} ${h} 0 0 0 0 ${s}z`,
  };
  if (kind === "dot") return <circle key={key} className={className} cx={x + h} cy={y + h} r={8} />;
  if (kind === "circle") return <circle key={key} className={className} cx={x + h} cy={y + h} r={h} />;
  if (kind === "square") return <rect key={key} className={className} x={x} y={y} width={s} height={s} />;
  if (kind === "bar") return <rect key={key} className={className} x={x} y={y} width={2 * s} height={s} />;
  return <path key={key} className={className} d={d[kind]} />;
}

export function BandArt({ name }: { name: string }) {
  return (
    <svg
      className="band-art"
      aria-hidden="true"
      viewBox={`0 0 ${CELL * COLS} ${CELL * ROWS}`}
      preserveAspectRatio="xMaxYMin slice"
    >
      {bandShapes(name).map(draw)}
    </svg>
  );
}
