/** Where a slow outside job stands (a research call, an import, a
 *  sync): queued, working, retrying, failed or done, each in words. A
 *  failure always shows, with its reason under the ⓘ of InfoTip, so a
 *  costly call isn't made twice because it looked never asked; a retry
 *  after a rate limit says "retrying", not "failed". Never the accent:
 *  working is a moving dot, not a colour. */
export type Job = "queued" | "running" | "retrying" | "failed" | "done";

const WORDS: Record<Job, string> = {
  queued: "queued",
  running: "working…",
  retrying: "retrying…",
  failed: "failed",
  done: "done",
};

export function JobStatus({ status, label }: { status?: Job; label?: Partial<Record<Job, string>> }) {
  if (!status) return null;
  const words = label?.[status] ?? WORDS[status];
  const kind = status === "failed" ? " bad" : status === "running" || status === "retrying" ? " busy" : "";
  return <span className={`pill job${kind}`}>{words}</span>;
}
