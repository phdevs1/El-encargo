interface ProgressBarProps {
  /** Position at join time — stable denominator. */
  initial: number;
  /** Current live position from polling. */
  current: number;
}

function clamp(min: number, max: number, value: number): number {
  return Math.min(max, Math.max(min, value));
}

export function ProgressBar({ initial, current }: ProgressBarProps) {
  const pct =
    initial <= 1 ? 100 : clamp(0, 100, Math.round(((initial - current) / (initial - 1)) * 100));

  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-border">
      <div
        className="h-full rounded-full bg-accent transition-[width] duration-500 ease-out"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
