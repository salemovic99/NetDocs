"use client";

import { motion } from "framer-motion";

import { pageVariants } from "@/lib/motion/variants";

// A template re-mounts on navigation, so this animates each route transition.
export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <motion.div initial="hidden" animate="visible" variants={pageVariants}>
      {children}
    </motion.div>
  );
}
