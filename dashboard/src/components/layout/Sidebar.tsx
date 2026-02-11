import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Command Center", icon: "\u2302" },
  { to: "/events", label: "Event Feed", icon: "\u26A0" },
  { to: "/networks", label: "Networks", icon: "\u25C9" },
  { to: "/convergence", label: "Convergence", icon: "\u2726" },
  { to: "/map", label: "Geographic", icon: "\u2316" },
  { to: "/thresholds", label: "Thresholds", icon: "\u2261" },
  { to: "/reports", label: "Reports", icon: "\u2193" },
];

export default function Sidebar() {
  return (
    <aside className="flex w-56 flex-col bg-smae-sidebar text-white">
      <div className="flex items-center gap-2 border-b border-white/10 px-4 py-4">
        <span className="text-lg font-bold tracking-tight text-white">SMAE</span>
        <span className="text-xs text-white/50">Dashboard</span>
      </div>
      <nav className="flex-1 py-2">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                isActive
                  ? "bg-white/10 text-white font-medium"
                  : "text-white/60 hover:bg-white/5 hover:text-white/90"
              }`
            }
          >
            <span className="w-4 text-center">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-white/10 px-4 py-3 text-xs text-white/30">
        Socio-Metabolic Analytical Engine v0.1
      </div>
    </aside>
  );
}
