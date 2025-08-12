import React, { useRef, useEffect } from 'react';
import { useVirtualization, useShouldVirtualize } from '../hooks/useVirtualization';

interface VirtualizedListProps<T> {
  items: T[];
  itemHeight: number;
  height: number;
  renderItem: (item: T, index: number) => React.ReactNode;
  className?: string;
  threshold?: number;
}

export function VirtualizedList<T>({
  items,
  itemHeight,
  height,
  renderItem,
  className = '',
  threshold = 100
}: VirtualizedListProps<T>) {
  const containerRef = useRef<HTMLDivElement>(null);
  const shouldVirtualize = useShouldVirtualize(items.length, threshold);
  
  const { virtualItems, totalHeight } = useVirtualization(items, {
    itemHeight,
    containerHeight: height
  });

  useEffect(() => {
    const container = containerRef.current;
    if (!container || !shouldVirtualize) return;

    const handleScroll = () => {
      // Scroll handling é feito internamente pelo hook
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [shouldVirtualize]);

  // Se não precisar virtualizar, renderiza lista normal
  if (!shouldVirtualize) {
    return (
      <div 
        className={`overflow-auto ${className}`} 
        style={{ height }}
        ref={containerRef}
      >
        {items.map((item, index) => (
          <div key={index} style={{ height: itemHeight }}>
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    );
  }

  // Lista virtualizada
  return (
    <div 
      id="virtual-container"
      ref={containerRef}
      className={`overflow-auto ${className}`}
      style={{ height }}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {virtualItems.map(({ index, start, item }) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              top: start,
              left: 0,
              right: 0,
              height: itemHeight
            }}
          >
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    </div>
  );
}

// Componente específico para listas de tickets
interface TicketListItem {
  id: string;
  title: string;
  status: string;
  priority: string;
  assignee?: string;
}

interface VirtualizedTicketListProps {
  tickets: TicketListItem[];
  height?: number;
  onTicketClick?: (ticket: TicketListItem) => void;
}

export function VirtualizedTicketList({
  tickets,
  height = 400,
  onTicketClick
}: VirtualizedTicketListProps) {
  const renderTicket = (ticket: TicketListItem, index: number) => (
    <div 
      className="flex items-center justify-between p-3 border-b hover:bg-gray-50 cursor-pointer"
      onClick={() => onTicketClick?.(ticket)}
    >
      <div className="flex-1">
        <h4 className="font-medium text-sm">{ticket.title}</h4>
        <p className="text-xs text-gray-500">#{ticket.id}</p>
      </div>
      <div className="flex items-center space-x-2">
        <span className={`px-2 py-1 text-xs rounded ${
          ticket.status === 'open' ? 'bg-red-100 text-red-800' :
          ticket.status === 'in-progress' ? 'bg-yellow-100 text-yellow-800' :
          'bg-green-100 text-green-800'
        }`}>
          {ticket.status}
        </span>
        {ticket.assignee && (
          <span className="text-xs text-gray-600">{ticket.assignee}</span>
        )}
      </div>
    </div>
  );

  return (
    <VirtualizedList
      items={tickets}
      itemHeight={60}
      height={height}
      renderItem={renderTicket}
      className="border rounded-lg"
    />
  );
}
