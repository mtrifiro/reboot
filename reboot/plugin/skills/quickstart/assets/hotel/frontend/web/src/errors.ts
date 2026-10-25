import { STATUS_LABEL } from "./rooms";

// One translator from a backend refusal to a sentence a person reads.
export function friendlyError(aborted: {
  error: { type: string } & Record<string, unknown>;
  message: string;
}): string {
  const e = aborted.error;
  switch (e.type) {
    case "RoomNotReadyError":
      return `This room isn't ready for a guest: it's ${
        STATUS_LABEL[String(e.status)]?.toLowerCase() ?? String(e.status)
      }. It has to be cleaned and inspected first.`;
    case "SameInspectorError":
      return `${String(e.cleanedByName) || "You"} cleaned this room, so someone else has to inspect it.`;
    case "InvalidTransitionError":
      return `That can't be done while the room is ${
        STATUS_LABEL[String(e.status)]?.toLowerCase() ?? String(e.status)
      }.`;
    case "MissingDetailError":
      return e.detail === "reason"
        ? "Say why the room is out of order."
        : e.detail === "room_type"
          ? "Choose a room type."
          : "Enter the guest's name.";
    case "SoldOutError":
      return `No ${String(e.roomType)} is left on the night of ${String(e.night)}.`;
    case "InvalidDatesError":
      return String(e.reason) || "Check the dates.";
    case "WrongRoomTypeError":
      return `The guest booked a ${String(e.booked)}; that room is a ${String(e.roomType)}.`;
    case "BookingStateError":
      return e.status === "checked_in"
        ? "The guest has already checked in."
        : `That booking is ${String(e.status).replace("_", " ")}.`;
    case "EarlyCheckInError":
      return `Check-in opens at ${String(e.checkInTime)} hotel time. Ask a manager to approve an early check-in.`;
    case "LastManagerError":
      return "The hotel needs at least one manager. Make someone else a manager first.";
    case "NotAMemberError":
      return "That person isn't on staff.";
    case "PermissionDenied":
      return "Your role doesn't allow that.";
    case "Unauthenticated":
      return "Sign in again to continue.";
    default:
      return aborted.message || "Something went wrong.";
  }
}
