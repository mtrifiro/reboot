export type Status =
  | "vacant_dirty"
  | "cleaning"
  | "vacant_clean"
  | "inspected"
  | "occupied"
  | "out_of_order";

export type Role = "" | "manager" | "front_desk" | "housekeeping";

// In the order a room moves through them, ready-to-sell first.
export const STATUSES: Status[] = [
  "inspected",
  "occupied",
  "vacant_dirty",
  "cleaning",
  "vacant_clean",
  "out_of_order",
];

export const STATUS_LABEL: Record<string, string> = {
  inspected: "Ready",
  occupied: "Occupied",
  vacant_dirty: "Dirty",
  cleaning: "Being cleaned",
  vacant_clean: "Clean, awaiting inspection",
  out_of_order: "Out of order",
};

export const STATUS_SHORT: Record<string, string> = {
  inspected: "Ready",
  occupied: "Occupied",
  vacant_dirty: "Dirty",
  cleaning: "Cleaning",
  vacant_clean: "To inspect",
  out_of_order: "Out of order",
};

export const ROLE_LABEL: Record<string, string> = {
  manager: "Manager",
  front_desk: "Front desk",
  housekeeping: "Housekeeping",
  "": "No role yet",
};

export const can = {
  clean: (r: Role) => r === "housekeeping" || r === "manager",
  frontDesk: (r: Role) => r === "front_desk" || r === "manager",
  manage: (r: Role) => r === "manager",
};

export function sinceText(iso: string): string {
  if (!iso) return "";
  const minutes = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} h ago`;
  return new Date(iso).toLocaleDateString();
}
