import { Menu } from "lucide-react";

export function Header({ onMenuClick }: { onMenuClick?: () => void }) {
  return (
    <header className="w-full bg-white border-b border-charcoal-200 px-4 sm:px-8 py-4 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-4">
        {onMenuClick && (
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 -ml-2 text-charcoal-500 hover:text-charcoal-900 rounded-lg hover:bg-charcoal-50 transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}
        <h1 className="text-lg font-serif font-semibold text-charcoal-900 tracking-tight">
          Dashboard
        </h1>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-right hidden sm:block">
          <div className="text-sm font-semibold text-charcoal-900">
            Donald Okonkwo
          </div>
          <div className="text-xs text-charcoal-500 font-medium">
            Administrator
          </div>
        </div>
        <img
          src="https://i.pravatar.cc/150?img=11"
          alt="profile"
          className="w-10 h-10 rounded-full border border-charcoal-200 object-cover shadow-xs"
        />
      </div>
    </header>
  );
}

export default Header;
