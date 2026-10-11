import { Link } from "react-router-dom";

/**
 * Reusable button with polished hover motion.
 * - variant: primary | secondary | ghost | danger
 * - as="link" + to=... renders a react-router Link
 * - icon / iconRight: react-icon components; they animate on hover
 */
const VARIANTS = {
  primary:
    "bg-gradient-to-b from-brand-500 to-brand-600 text-white shadow-sm shadow-brand-600/30 hover:from-brand-500 hover:to-brand-700 hover:shadow-md hover:shadow-brand-600/40",
  secondary:
    "border border-slate-200 bg-white text-slate-700 shadow-sm hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700",
  ghost:
    "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
  danger:
    "border border-red-200 bg-white text-red-600 hover:border-red-300 hover:bg-red-50",
};

const SIZES = {
  sm: "px-3 py-1.5 text-xs gap-1.5",
  md: "px-4 py-2.5 text-sm gap-2",
  lg: "px-5 py-3 text-base gap-2.5",
};

export default function Button({
  children,
  variant = "primary",
  size = "md",
  icon: Icon,
  iconRight: IconRight,
  as,
  to,
  className = "",
  ...props
}) {
  const base =
    "group inline-flex items-center justify-center rounded-xl font-semibold " +
    "transition-all duration-200 active:translate-y-px disabled:opacity-50 " +
    "disabled:pointer-events-none focus-visible:outline-none " +
    "focus-visible:ring-2 focus-visible:ring-brand-400 focus-visible:ring-offset-1 " +
    "hover:-translate-y-0.5";
  const cls = `${base} ${VARIANTS[variant]} ${SIZES[size]} ${className}`;

  const content = (
    <>
      {Icon && (
        <Icon className="transition-transform duration-200 group-hover:-translate-x-0.5 group-hover:scale-110" />
      )}
      {children}
      {IconRight && (
        <IconRight className="transition-transform duration-200 group-hover:translate-x-1" />
      )}
    </>
  );

  if (as === "link") {
    return (
      <Link to={to} className={cls} {...props}>
        {content}
      </Link>
    );
  }
  return (
    <button className={cls} {...props}>
      {content}
    </button>
  );
}
