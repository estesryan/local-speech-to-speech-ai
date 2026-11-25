import {
  MODEL_STATUS_LABEL,
  type ModelConnectionStatus,
} from "@/lib/backend/model-status";
import { cn } from "@/lib/utils";

/** "● Local model", the header's status cluster, reporting the real backend connection. */
export function ModelStatus({ status }: { status: ModelConnectionStatus }) {
  const label = MODEL_STATUS_LABEL[status];
  return (
    <output
      className="flex items-center gap-2.5 text-sm text-app-slate"
      aria-label={`Local model: ${label}`}
    >
      <span
        aria-hidden="true"
        className={cn(
          "size-2.5 rounded-full",
          status === "connected" && "bg-app-mint",
          status === "connecting" && "bg-app-mint/60 motion-safe:animate-pulse",
          status === "not-connected" && "border border-app-slate/60",
          status === "error" && "bg-app-coral",
        )}
      />
      <span>Local model</span>
      <span className="text-app-slate/60">·</span>
      <span className="text-app-slate/80">{label}</span>
    </output>
  );
}
