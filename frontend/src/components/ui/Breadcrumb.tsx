import React from 'react';
import { ChevronRight, Home } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ComponentType<{ className?: string }>;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
  separator?: React.ReactNode;
  showHomeIcon?: boolean;
}

export const Breadcrumb = React.memo<BreadcrumbProps>(function Breadcrumb({
  items,
  className,
  separator = <ChevronRight className='w-4 h-4 text-muted-foreground' />,
  showHomeIcon = true,
}) {
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <nav
      aria-label='Breadcrumb'
      className={cn('flex items-center space-x-2 text-sm', className)}
    >
      <ol className='flex items-center space-x-2'>
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          const Icon = item.icon;
          const isHome = index === 0 && showHomeIcon;

          return (
            <li key={item.href || index} className='flex items-center space-x-2'>
              {index > 0 && (
                <span className='flex items-center' aria-hidden='true'>
                  {separator}
                </span>
              )}
              
              {item.href && !isLast ? (
                <a
                  href={item.href}
                  className={cn(
                    'flex items-center space-x-1 text-muted-foreground hover:text-foreground transition-colors',
                    'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded-sm px-1 py-0.5'
                  )}
                >
                  {isHome && showHomeIcon ? (
                    <Home className='w-4 h-4' />
                  ) : Icon ? (
                    <Icon className='w-4 h-4' />
                  ) : null}
                  <span>{item.label}</span>
                </a>
              ) : (
                <span
                  className={cn(
                    'flex items-center space-x-1',
                    isLast ? 'text-foreground font-medium' : 'text-muted-foreground'
                  )}
                  aria-current={isLast ? 'page' : undefined}
                >
                  {isHome && showHomeIcon ? (
                    <Home className='w-4 h-4' />
                  ) : Icon ? (
                    <Icon className='w-4 h-4' />
                  ) : null}
                  <span>{item.label}</span>
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
});

// Componente de conveniência para breadcrumbs simples
export const SimpleBreadcrumb = React.memo<{
  path: string;
  className?: string;
}>(function SimpleBreadcrumb({ path, className }) {
  const pathSegments = path.split('/').filter(Boolean);
  
  const items: BreadcrumbItem[] = [
    { label: 'Home', href: '/' },
    ...pathSegments.map((segment, index) => {
      const href = '/' + pathSegments.slice(0, index + 1).join('/');
      const label = segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
      
      return {
        label,
        href: index === pathSegments.length - 1 ? undefined : href,
      };
    }),
  ];

  return <Breadcrumb items={items} className={className} />;
});