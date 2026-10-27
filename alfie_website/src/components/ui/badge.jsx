import * as React from "react";
import { cva } from "class-variance-authority";
import { cn } from "../../lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default:
          "bg-blue-50 text-blue-700 border border-blue-200/80",
        secondary:
          "bg-zinc-100 text-zinc-800 border border-zinc-200/60",
        success:
          "bg-emerald-50 text-emerald-700 border border-emerald-200/80",
        warning:
          "bg-amber-50 text-amber-800 border border-amber-200/80",
        destructive:
          "bg-rose-50 text-rose-700 border border-rose-200/80",
        outline:
          "text-zinc-700 border border-zinc-200 bg-white shadow-xs",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

function Badge({ className, variant, ...props }) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
