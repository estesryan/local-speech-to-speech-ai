import { cn } from "@/lib/utils";

/** The app title as a wordmark: Inter 700, white, tight tracking (-1.5 at 45px). */
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
