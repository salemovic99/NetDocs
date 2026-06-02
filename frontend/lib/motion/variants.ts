import type { Variants, Transition } from "framer-motion";

export const easeOut: Transition = { duration: 0.25, ease: [0.22, 1, 0.36, 1] };

/** Page-level fade + subtle rise (used by route template). */
export const pageVariants: Variants = {
  hidden: { opacity: 0, y: 8 },
  visible: { opacity: 1, y: 0, transition: easeOut },
};

/** Container that staggers its children (lists, card grids). */
export const staggerContainer: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.04 } },
};

/** Individual list/row/card item. */
export const fadeUpItem: Variants = {
  hidden: { opacity: 0, y: 6 },
  visible: { opacity: 1, y: 0, transition: easeOut },
};

/** Scale/fade for popovers and modal-like surfaces. */
export const popVariants: Variants = {
  hidden: { opacity: 0, scale: 0.97 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.15 } },
};
