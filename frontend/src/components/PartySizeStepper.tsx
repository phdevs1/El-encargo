interface PartySizeStepperProps {
  value: number;
  onChange: (next: number) => void;
  min?: number;
  max?: number;
}

export function PartySizeStepper({ value, onChange, min = 1, max = 30 }: PartySizeStepperProps) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-border bg-surface px-3 py-2">
      <button
        type="button"
        aria-label="Menos"
        onClick={() => onChange(Math.max(min, value - 1))}
        disabled={value <= min}
        className="h-8 w-8 rounded-md text-lg text-text disabled:opacity-30"
      >
        −
      </button>
      <span className="text-base font-medium text-text">{value}</span>
      <button
        type="button"
        aria-label="Más"
        onClick={() => onChange(Math.min(max, value + 1))}
        disabled={value >= max}
        className="h-8 w-8 rounded-md text-lg text-text disabled:opacity-30"
      >
        +
      </button>
    </div>
  );
}
