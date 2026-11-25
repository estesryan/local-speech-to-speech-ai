import { cn } from "@/lib/utils";

/** The app title shown in the header. */
export function Wordmark({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "font-bold tracking-[-0.033em] text-app-ink select-none",
        className,
      )}
    >
      Local Speech-to-Speech
    </span>
  );
}
