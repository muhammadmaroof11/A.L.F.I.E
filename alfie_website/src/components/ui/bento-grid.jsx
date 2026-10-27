import React from "react";
import { ArrowRight } from "lucide-react";
import { cn } from "../../lib/utils";
import { CardSpotlight } from "./spotlight";

export function BentoGrid({
  children,
  className,
}) {
  return (
    <div
      className={cn(
        "grid w-full grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 max-w-7xl mx-auto",
        className
      )}
    >
      {children}
    </div>
  );
}

export function BentoCard({
  name,
  className,
  background,
  Icon,
  description,
  cta,
  badge,
  onClick,
  stat,
}) {
  return (
    <CardSpotlight
      key={name}
      onClick={onClick}
      className={cn(
        "group relative col-span-1 flex flex-col justify-between overflow-hidden cursor-pointer",
        "border border-white/[0.08] hover:border-[#38BDF8]/40 hover:shadow-[0_0_30px_rgba(56,189,248,0.15)]",
        className
      )}
    >
      {/* Background Graphic or 3D viewport */}
      <div className="absolute inset-0 z-0 opacity-40 transition-opacity duration-300 group-hover:opacity-70">
        {background}
      </div>

      {/* Top Header info */}
      <div className="relative z-10 flex items-center justify-between w-full mb-6">
        <div className="flex items-center gap-3">
          {Icon && (
            <div className="p-2.5 rounded-xl bg-white/[0.05] border border-white/[0.1] text-[#38BDF8] group-hover:bg-[#38BDF8]/20 group-hover:border-[#38BDF8]/40 transition-colors">
              <Icon className="h-5 w-5" />
            </div>
          )}
          {badge && (
            <span className="text-[11px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-[#38BDF8]/10 text-[#38BDF8] border border-[#38BDF8]/30">
              {badge}
            </span>
          )}
        </div>

        {stat && (
          <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
            {stat}
          </span>
        )}
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col gap-2 mt-auto">
        <h3 className="text-xl font-bold tracking-tight text-white font-heading group-hover:text-[#38BDF8] transition-colors">
          {name}
        </h3>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-normal">
          {description}
        </p>
        
        {cta && (
          <div className="flex items-center gap-1.5 text-xs font-bold text-[#38BDF8] mt-3 group-hover:translate-x-1 transition-transform">
            <span>{cta}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        )}
      </div>
    </CardSpotlight>
  );
}
