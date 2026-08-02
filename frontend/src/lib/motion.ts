import { Variants, Transition } from "framer-motion";

export const springConfig: Transition = {
  type: "spring",
  stiffness: 300,
  damping: 30,
};

export const pageTransition: Variants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0, transition: springConfig },
  exit: { opacity: 0, y: -10, transition: { duration: 0.2 } },
};

export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: 0.3 } },
  exit: { opacity: 0, transition: { duration: 0.2 } },
};

export const slideUp: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: springConfig },
  exit: { opacity: 0, y: 20, transition: { duration: 0.2 } },
};

export const scaleIn: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1, transition: springConfig },
  exit: { opacity: 0, scale: 0.95, transition: { duration: 0.2 } },
};

export const panelCollapseHorizontal: Variants = {
  expanded: { width: "auto", opacity: 1, transition: springConfig },
  collapsed: { width: 0, opacity: 0, transition: springConfig },
};

export const panelCollapseVertical: Variants = {
  expanded: { height: "auto", opacity: 1, transition: springConfig },
  collapsed: { height: 0, opacity: 0, transition: springConfig },
};
