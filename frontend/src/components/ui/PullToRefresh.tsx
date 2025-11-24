/**
 * Pull-to-Refresh Component
 * Implements native-like pull-to-refresh gesture for mobile
 */

import React, { useState, useRef, useCallback, ReactNode } from 'react';
import { RefreshCw } from 'lucide-react';

interface PullToRefreshProps {
    onRefresh: () => Promise<void>;
    children: ReactNode;
    threshold?: number;
    maxPullDistance?: number;
}

export const PullToRefresh: React.FC<PullToRefreshProps> = ({
    onRefresh,
    children,
    threshold = 80,
    maxPullDistance = 150
}) => {
    const [pullDistance, setPullDistance] = useState(0);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [canRefresh, setCanRefresh] = useState(false);

    const startY = useRef(0);
    const containerRef = useRef<HTMLDivElement>(null);

    const handleTouchStart = useCallback((e: React.TouchEvent) => {
        // Only allow pull-to-refresh when scrolled to top
        if (containerRef.current && containerRef.current.scrollTop === 0) {
            startY.current = e.touches[0].clientY;
        }
    }, []);

    const handleTouchMove = useCallback((e: React.TouchEvent) => {
        if (startY.current === 0 || isRefreshing) return;

        const currentY = e.touches[0].clientY;
        const distance = currentY - startY.current;

        // Only track downward pulls
        if (distance > 0) {
            // Prevent default scroll behavior
            e.preventDefault();

            // Apply resistance to pull
            const resistedDistance = Math.min(
                distance * 0.5, // 50% resistance
                maxPullDistance
            );

            setPullDistance(resistedDistance);
            setCanRefresh(resistedDistance >= threshold);
        }
    }, [isRefreshing, threshold, maxPullDistance]);

    const handleTouchEnd = useCallback(async () => {
        if (canRefresh && !isRefreshing) {
            setIsRefreshing(true);

            try {
                await onRefresh();
            } catch (error) {
                console.error('Refresh failed:', error);
            } finally {
                setIsRefreshing(false);
                setPullDistance(0);
                setCanRefresh(false);
                startY.current = 0;
            }
        } else {
            // Reset if not past threshold
            setPullDistance(0);
            setCanRefresh(false);
            startY.current = 0;
        }
    }, [canRefresh, isRefreshing, onRefresh]);

    const pullProgress = Math.min((pullDistance / threshold) * 100, 100);
    const rotation = (pullDistance / threshold) * 360;

    return (
        <div
            ref={containerRef}
            className="relative overflow-auto h-full"
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
            style={{
                touchAction: pullDistance > 0 ? 'none' : 'auto'
            }}
        >
            {/* Pull indicator */}
            <div
                className="absolute top-0 left-0 right-0 flex items-center justify-center transition-all duration-200"
                style={{
                    height: `${pullDistance}px`,
                    opacity: pullDistance > 0 ? 1 : 0,
                    transform: `translateY(-${Math.max(0, 60 - pullDistance)}px)`
                }}
            >
                <div className="flex flex-col items-center gap-2">
                    <div
                        className={`
              relative w-12 h-12 rounded-full flex items-center justify-center
              ${canRefresh ? 'bg-blue-500' : 'bg-gray-300'}
              transition-colors duration-200
            `}
                    >
                        <RefreshCw
                            className={`
                h-6 w-6 text-white transition-transform duration-200
                ${isRefreshing ? 'animate-spin' : ''}
              `}
                            style={{
                                transform: isRefreshing ? undefined : `rotate(${rotation}deg)`
                            }}
                        />
                    </div>

                    <p className={`
            text-xs font-medium transition-colors duration-200
            ${canRefresh ? 'text-blue-600' : 'text-gray-500'}
          `}>
                        {isRefreshing ? 'Refreshing...' : canRefresh ? 'Release to refresh' : 'Pull to refresh'}
                    </p>

                    {/* Progress indicator */}
                    {!isRefreshing && pullDistance > 0 && (
                        <div className="w-20 h-1 bg-gray-200 rounded-full overflow-hidden">
                            <div
                                className={`h-full transition-all duration-100 ${canRefresh ? 'bg-blue-500' : 'bg-gray-400'}`}
                                style={{ width: `${pullProgress}%` }}
                            />
                        </div>
                    )}
                </div>
            </div>

            {/* Content */}
            <div
                style={{
                    transform: `translateY(${pullDistance}px)`,
                    transition: pullDistance === 0 ? 'transform 0.3s ease-out' : 'none'
                }}
            >
                {children}
            </div>
        </div>
    );
};

export default PullToRefresh;
