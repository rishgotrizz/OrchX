"use client";
import { motion } from "framer-motion";
import * as React from "react";

export function PageTransition({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="h-full w-full"
    >
      {children}
    </motion.div>
  );
}
