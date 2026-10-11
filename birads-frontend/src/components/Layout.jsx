import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { FiLayers, FiLogOut, FiPlus, FiPlusCircle, FiUser } from "react-icons/fi";
import { useAuth } from "@/hooks/useAuth";
import Brand from "@/components/Brand";
import Button from "@/components/Button";
import ChatWidget from "@/components/ChatWidget";
import Footer from "@/components/Footer";

// Full set (used for the mobile nav row).
const navItems = [
  { to: "/worklist", label: "Worklist", icon: FiLayers, end: false },
  { to: "/study", label: "New study", icon: FiPlusCircle, end: false },
];
// Desktop top-tabs: "New study" lives in the CTA button, so only show Worklist here.
const desktopNav = navItems.slice(0, 1);

function NavItem({ to, label, icon: Icon, end }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `group relative flex items-center gap-2 rounded-lg px-3.5 py-2 text-sm font-semibold transition-colors ${
          isActive ? "text-white" : "text-brand-100/70 hover:text-white"
        }`
      }
    >
      {({ isActive }) => (
        <>
          <Icon
            className={`transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:scale-110 ${
              isActive ? "text-brand-300" : ""
            }`}
          />
          {label}
          {/* Animated underline: full when active, grows from center on hover */}
          <span
            className={`pointer-events-none absolute inset-x-3 -bottom-[7px] h-0.5 rounded-full bg-brand-300 transition-all duration-300 ${
              isActive
                ? "scale-x-100 opacity-100"
                : "scale-x-0 opacity-0 group-hover:scale-x-100 group-hover:opacity-70"
            }`}
          />
        </>
      )}
    </NavLink>
  );
}

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen flex-col bg-[#f1f5f4]">
      <header className="no-print sticky top-0 z-20 border-b border-brand-800/60 bg-gradient-to-r from-brand-900 to-brand-800 shadow-md shadow-brand-900/20">
        {/* Premium gradient accent strip */}
        <div className="h-1 w-full bg-gradient-to-r from-brand-300 via-brand-500 to-brand-700" />

        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
          {/* Left: brand + primary nav */}
          <div className="flex items-center gap-4">
            <Link to="/" className="transition-opacity hover:opacity-90">
              <Brand size={34} subtitle light />
            </Link>
            <div className="mx-1 hidden h-9 w-px bg-white/15 sm:block" />
            <nav className="hidden items-center gap-1 sm:flex">
              {desktopNav.map((item) => (
                <NavItem key={item.to} {...item} />
              ))}
            </nav>
          </div>

          {/* Right: status + CTA + user + logout */}
          <div className="flex items-center gap-2 sm:gap-4">
            <span
              title="All services operational"
              className="hidden items-center gap-1.5 text-[11px] font-semibold text-brand-200/80 lg:inline-flex"
            >
              <span className="relative flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-300 opacity-75" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400" />
              </span>
              Operational
            </span>

            <Button
              as="link"
              to="/study"
              size="sm"
              variant="secondary"
              icon={FiPlus}
              className="hidden md:inline-flex"
            >
              New study
            </Button>

            <div className="hidden h-9 w-px bg-white/15 sm:block" />

            {/* User + sign out */}
            <div className="flex items-center gap-3">
              <div className="hidden text-right leading-tight sm:block">
                <div className="text-sm font-semibold text-white">
                  {user?.name}
                </div>
                <div className="flex items-center justify-end gap-1 text-[10px] font-medium uppercase tracking-wider text-brand-200/70">
                  <FiUser size={10} /> {user?.role ?? "radiologist"}
                </div>
              </div>
              {user?.picture ? (
                <img
                  src={user.picture}
                  alt={user.name}
                  className="h-9 w-9 rounded-full object-cover ring-2 ring-white/25"
                />
              ) : (
                <span className="grid h-9 w-9 place-items-center rounded-full bg-white/15 text-sm font-bold text-white ring-1 ring-white/20">
                  {user?.name?.[0] ?? "?"}
                </span>
              )}
              <button
                onClick={() => {
                  logout();
                  navigate("/login");
                }}
                title="Sign out"
                className="group flex items-center gap-1.5 rounded-lg px-2.5 py-2 text-sm font-semibold text-brand-100 ring-1 ring-white/15 transition-colors hover:bg-red-500/20 hover:text-white hover:ring-red-300/30"
              >
                <FiLogOut className="transition-transform duration-200 group-hover:translate-x-0.5" />
                <span className="hidden lg:inline">Sign out</span>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile nav row */}
        <nav className="flex gap-1 border-t border-white/10 px-3 py-1.5 sm:hidden">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex flex-1 items-center justify-center gap-1.5 rounded-lg px-3 py-2 text-xs font-semibold transition ${
                  isActive
                    ? "bg-white/15 text-white"
                    : "text-brand-100/80 hover:bg-white/10"
                }`
              }
            >
              <Icon /> {label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 sm:py-8">
        {children ?? <Outlet />}
      </main>

      <Footer />
      <ChatWidget />
    </div>
  );
}
