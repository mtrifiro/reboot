// The one translator from a typed backend error to what the user
// reads. `aborted.error.type` is the Python error class's name; the
// fields on each case are the error model's, camelCased. Add one case
// per error the API declares, above `PermissionDenied`.
export function friendlyError(aborted: {
  error: { type: string } & Record<string, unknown>;
  message: string;
}): string {
  switch (aborted.error.type) {
    // case "QuotaExceededError":
    //   return `Limit reached (${String(aborted.error.limit)}).`;
    case "PermissionDenied":
      return "You don't have access to do that.";
    default:
      return aborted.message || `Something went wrong.`;
  }
}
