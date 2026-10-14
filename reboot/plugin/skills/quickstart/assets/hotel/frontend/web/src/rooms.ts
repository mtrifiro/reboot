export type Status = "clean" | "occupied" | "dirty";

// Ready to sell first.
export const STATUSES: Status[] = ["clean", "occupied", "dirty"];

export const STATUS_LABEL: Record<string, string> = {
  clean: "Ready",
  occupied: "Occupied",
  dirty: "Dirty",
};
