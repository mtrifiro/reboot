import { STATUS_LABEL } from "./rooms";

// One translator from a backend refusal to a sentence a person reads.
export function friendlyError(aborted: {
  error: { type: string } & Record<string, unknown>;
  message: string;
}): string {
  const e = aborted.error;
  const status = STATUS_LABEL[String(e.status)]?.toLowerCase() ?? String(e.status);
  switch (e.type) {
    case "RoomNotReadyError":
      return `This room can't take a guest: it's ${status}. A guest is checked in only to a clean room.`;
    case "InvalidTransitionError":
      return `That can't be done while the room is ${status}.`;
    case "MissingGuestNameError":
      return "Enter the guest's name.";
    default:
      return aborted.message || "Something went wrong.";
  }
}
