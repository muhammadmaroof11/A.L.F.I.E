import React, { createContext, useContext, useState } from "react";
import { ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { cn } from "../../lib/utils";

const AccordionContext = createContext({
  activeItems: [],
  toggleItem: () => {},
  type: "single",
});

export function Accordion({
  children,
  type = "single",
  collapsible = true,
  defaultValue,
  className,
}) {
  const [activeItems, setActiveItems] = useState(
    defaultValue ? (Array.isArray(defaultValue) ? defaultValue : [defaultValue]) : []
  );

  const toggleItem = (val) => {
    if (type === "single") {
      if (activeItems.includes(val)) {
        if (collapsible) setActiveItems([]);
      } else {
        setActiveItems([val]);
      }
    } else {
      if (activeItems.includes(val)) {
        setActiveItems(activeItems.filter((i) => i !== val));
      } else {
        setActiveItems([...activeItems, val]);
      }
    }
  };

  return (
    <AccordionContext.Provider value={{ activeItems, toggleItem, type }}>
      <div className={cn("space-y-3", className)}>{children}</div>
    </AccordionContext.Provider>
  );
}

export function AccordionItem({ value, children, className }) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-zinc-200/80 bg-white shadow-xs overflow-hidden transition-all duration-200",
        className
      )}
    >
      {React.Children.map(children, (child) =>
        React.isValidElement(child) ? React.cloneElement(child, { value }) : child
      )}
    </div>
  );
}

export function AccordionTrigger({ value, children, className }) {
  const { activeItems, toggleItem } = useContext(AccordionContext);
  const isOpen = activeItems.includes(value);

  return (
    <button
      type="button"
      onClick={() => toggleItem(value)}
      className={cn(
        "flex w-full items-center justify-between p-5 text-left text-sm sm:text-base font-bold text-zinc-900 transition-all hover:text-blue-600 cursor-pointer",
        className
      )}
    >
      <span>{children}</span>
      <ChevronDown
        className={cn(
          "h-4 w-4 shrink-0 text-zinc-400 transition-transform duration-200",
          isOpen && "rotate-180 text-blue-600"
        )}
      />
    </button>
  );
}

export function AccordionContent({ value, children, className }) {
  const { activeItems } = useContext(AccordionContext);
  const isOpen = activeItems.includes(value);

  return (
    <AnimatePresence initial={false}>
      {isOpen && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="overflow-hidden"
        >
          <div className={cn("p-5 pt-0 text-xs sm:text-sm text-zinc-600 leading-relaxed", className)}>
            {children}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
