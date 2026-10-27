import React, { createContext, useContext, useState } from "react";
import { motion } from "motion/react";
import { cn } from "../../lib/utils";

const TabsContext = createContext({
  activeTab: "",
  setActiveTab: () => {},
});

export function Tabs({
  defaultValue,
  value,
  onValueChange,
  children,
  className,
}) {
  const [selected, setSelected] = useState(defaultValue || "");
  const activeTab = value !== undefined ? value : selected;

  const handleTabChange = (val) => {
    if (onValueChange) onValueChange(val);
    else setSelected(val);
  };

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab: handleTabChange }}>
      <div className={cn("flex flex-col gap-4", className)}>{children}</div>
    </TabsContext.Provider>
  );
}

export function TabsList({ children, className }) {
  return (
    <div
      className={cn(
        "inline-flex items-center justify-center rounded-2xl bg-[#080D1A]/90 p-1.5 border border-white/[0.08] backdrop-blur-xl",
        className
      )}
    >
      {children}
    </div>
  );
}

export function TabsTrigger({ value, children, className }) {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  const isActive = activeTab === value;

  return (
    <button
      type="button"
      onClick={() => setActiveTab(value)}
      className={cn(
        "relative z-10 inline-flex items-center justify-center whitespace-nowrap rounded-xl px-4 py-2 text-xs sm:text-sm font-bold transition-colors cursor-pointer",
        isActive ? "text-white" : "text-slate-400 hover:text-slate-200",
        className
      )}
    >
      {isActive && (
        <motion.div
          layoutId="activeTabIndicator"
          className="absolute inset-0 z-[-1] rounded-xl bg-gradient-to-r from-[#0284C7] to-[#38BDF8] shadow-[0_0_20px_rgba(56,189,248,0.4)]"
          transition={{ type: "spring", stiffness: 400, damping: 30 }}
        />
      )}
      {children}
    </button>
  );
}

export function TabsContent({ value, children, className }) {
  const { activeTab } = useContext(TabsContext);
  if (activeTab !== value) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.25 }}
      className={cn("w-full", className)}
    >
      {children}
    </motion.div>
  );
}
