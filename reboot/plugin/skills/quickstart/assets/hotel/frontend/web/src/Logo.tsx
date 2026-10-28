// An arched door with a keyhole: the hotel room, in the accent.
export function Logo() {
  return (
    <svg
      viewBox="0 0 32 32"
      width="22"
      height="22"
      aria-hidden="true"
      style={{ verticalAlign: "-5px", marginRight: 8 }}
    >
      <path
        fill="currentColor"
        d="M6 30V13a10 10 0 0 1 20 0v17h-4V13a6 6 0 0 0-12 0v17z"
      />
      <circle cx="16" cy="19" r="2.5" fill="currentColor" />
      <rect x="15" y="20" width="2" height="5" rx="1" fill="currentColor" />
    </svg>
  );
}
