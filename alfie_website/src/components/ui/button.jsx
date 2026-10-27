import * as React from "react";
import { cva } from "class-variance-authority";
import { cn } from "../../lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-medium transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 cursor-pointer select-none",
  {
    variants: {
      variant: {
        default:
          "bg-[#008BC5] text-white hover:bg-[#007cae] shadow-sm border border-[#008BC5]/20 font-semibold active:scale-[0.98]",
        primary:
          "bg-[#008BC5] text-white hover:bg-[#007cae] shadow-sm border border-[#008BC5]/20 font-semibold active:scale-[0.98]",
        secondary:
          "bg-slate-100 text-slate-800 hover:bg-slate-200 border border-slate-200/60 shadow-xs",
        outline:
          "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:text-slate-900 hover:border-slate-300 shadow-xs",
        dark:
          "bg-[#1D293D] text-white hover:bg-[#162031] shadow-sm border border-[#1D293D]/20 font-semibold active:scale-[0.98]",
        emerald:
          "bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm font-semibold",
        ghost:
          "text-slate-600 hover:text-slate-900 hover:bg-slate-100",
        destructive:
          "bg-rose-600 text-white hover:bg-rose-700 shadow-sm font-semibold",
        shimmer:
          "bg-[#008BC5] text-white hover:bg-[#007cae] shadow-sm font-semibold",
      },
      size: {
        default: "h-11 px-5 py-2.5",
        sm: "h-9 rounded-lg px-3.5 text-xs font-medium",
        lg: "h-12 rounded-xl px-6 text-sm font-semibold",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

const Button = React.forwardRef(({ className, variant, size, ...props }, ref) => {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  );
});
Button.displayName = "Button";

export { Button, buttonVariants };
