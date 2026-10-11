import { useEffect, useRef, useState } from "react";

/**
 * Fades + slides children into view the first time they cross the viewport.
 * Zero dependencies — plain IntersectionObserver.
 */
export default function Reveal({
  children,
  delay = 0,
  y = 16,
  className = "",
  as: Tag = "div",
}) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          obs.disconnect();
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  return (
    <Tag
      ref={ref}
      style={{
        transitionDelay: `${delay}ms`,
        transform: visible ? "translateY(0)" : `translateY(${y}px)`,
      }}
      className={`transition-all duration-700 ease-out ${
        visible ? "opacity-100" : "opacity-0"
      } ${className}`}
    >
      {children}
    </Tag>
  );
}
