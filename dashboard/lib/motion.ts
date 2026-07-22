import type { Variants } from "framer-motion"

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] },
  },
}

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.5, ease: "easeOut" },
  },
}

export const staggerContainer: Variants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
}

export const scaleOnHover = {
  whileHover: { y: -4, transition: { duration: 0.2 } },
  whileTap: { scale: 0.98 },
}

export const cardHover = {
  whileHover: {
    y: -6,
    boxShadow: "0 20px 40px -12px rgba(0, 0, 0, 0.08)",
    transition: { duration: 0.25, ease: "easeOut" },
  },
}
