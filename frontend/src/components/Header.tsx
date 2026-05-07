'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { href: '/latest', label: '最新' },
  { href: '/featured', label: '精选' },
  { href: '/archive', label: '归档' },
];

export default function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b" style={{ background: 'rgba(253,250,243,0.92)', backdropFilter: 'blur(12px)', borderColor: 'var(--divider)' }}>
      <div className="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link href="/latest" className="flex items-center gap-2.5 group no-underline">
          <span className="text-xl transition-transform group-hover:scale-110 duration-200">🏺</span>
          <span className="font-serif font-bold text-lg tracking-wider" style={{ color: 'var(--fg)' }}>
            金文速递
          </span>
          <span className="hidden sm:inline text-[11px] tracking-widest px-2 py-0.5 rounded uppercase" style={{ color: 'var(--fg-muted)', background: 'var(--bronze-bg)', letterSpacing: '0.1em' }}>
            Jinwen
          </span>
        </Link>

        <nav className="flex items-center gap-0.5">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 no-underline',
                  isActive
                    ? ''
                    : 'hover:opacity-80'
                )}
                style={isActive ? {
                  background: 'var(--bronze-bg)',
                  color: 'var(--bronze-dark)',
                } : {
                  color: 'var(--fg-muted)',
                }}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
