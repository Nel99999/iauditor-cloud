/**
 * OfflineIndicator Component
 * Shows connection status and sync queue information
 */

import React from 'react';
import { useOfflineSync } from '../../hooks/useOfflineSync';
import { Alert, AlertDescription } from './alert';
import { Button } from './button';
import { Badge } from './badge';
import { WifiOff, Wifi, RefreshCw, CheckCircle, AlertTriangle, Clock } from 'lucide-react';

export const OfflineIndicator: React.FC = () => {
    const { isOnline, isSyncing, pendingCount, lastSyncTime, error, syncNow } = useOfflineSync();

    // Don't show anything if online and no pending operations
    if (isOnline && pendingCount === 0 && !error) {
        return null;
    }

    const formatLastSyncTime = (timestamp: number | null) => {
        if (!timestamp) return 'Never';

        const seconds = Math.floor((Date.now() - timestamp) / 1000);
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        return `${Math.floor(seconds / 86400)}d ago`;
    };

    return (
        <div className="fixed bottom-4 right-4 z-50 max-w-md">
            <Alert className={`
        ${isOnline ? 'bg-blue-50 border-blue-200' : 'bg-amber-50 border-amber-200'}
        shadow-lg
      `}>
                <div className="flex items-start gap-3">
                    {/* Icon */}
                    <div className={`mt-0.5 ${isOnline ? 'text-blue-600' : 'text-amber-600'}`}>
                        {isOnline ? <Wifi className="h-5 w-5" /> : <WifiOff className="h-5 w-5" />}
                    </div>

                    {/* Content */}
                    <div className="flex-1 space-y-2">
                        <div className="flex items-center justify-between">
                            <div className={`font-semibold text-sm ${isOnline ? 'text-blue-900' : 'text-amber-900'}`}>
                                {isOnline ? 'Back Online' : 'You\'re Offline'}
                            </div>
                            <Badge variant={isOnline ? 'default' : 'secondary'} className="ml-2">
                                {pendingCount} pending
                            </Badge>
                        </div>

                        <AlertDescription className={isOnline ? 'text-blue-800' : 'text-amber-800'}>
                            {isOnline ? (
                                <span>
                                    {isSyncing ? 'Syncing changes...' : pendingCount > 0 ? 'Ready to sync changes' : 'All changes synced'}
                                </span>
                            ) : (
                                <span>
                                    Changes will sync automatically when you're back online. You can continue working.
                                </span>
                            )}
                        </AlertDescription>

                        {/* Error Message */}
                        {error && (
                            <div className="flex items-start gap-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-800">
                                <AlertTriangle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                                <span>{error}</span>
                            </div>
                        )}

                        {/* Last Sync Time */}
                        {lastSyncTime && (
                            <div className="flex items-center gap-1.5 text-xs text-gray-600">
                                <Clock className="h-3 w-3" />
                                <span>Last synced: {formatLastSyncTime(lastSyncTime)}</span>
                            </div>
                        )}

                        {/* Actions */}
                        {isOnline && pendingCount > 0 && (
                            <div className="flex gap-2 mt-2">
                                <Button
                                    size="sm"
                                    onClick={syncNow}
                                    disabled={isSyncing}
                                    className="h-8"
                                >
                                    {isSyncing ? (
                                        <>
                                            <RefreshCw className="h-3 w-3 mr-1.5 animate-spin" />
                                            Syncing...
                                        </>
                                    ) : (
                                        <>
                                            <CheckCircle className="h-3 w-3 mr-1.5" />
                                            Sync Now
                                        </>
                                    )}
                                </Button>
                            </div>
                        )}
                    </div>
                </div>
            </Alert>
        </div>
    );
};

export default OfflineIndicator;
