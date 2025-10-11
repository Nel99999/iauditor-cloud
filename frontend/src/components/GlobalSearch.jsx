import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Search, X, FileText, CheckSquare, Users, Folder, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const GlobalSearch = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const navigate = useNavigate();

  const performSearch = useCallback(async (searchQuery) => {
    if (searchQuery.length < 2) {
      setResults([]);
      return;
    }

    try {
      setLoading(true);
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      const response = await axios.get(
        `${API_BASE_URL}/api/search/global?query=${encodeURIComponent(searchQuery)}`,
        { headers }
      );

      setResults(response.data.results || []);
      setSelectedIndex(0);
    } catch (err) {
      console.error('Error performing search:', err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (query) {
        performSearch(query);
      } else {
        setResults([]);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [query, performSearch]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) {
        // Open modal with Cmd+K or Ctrl+K
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
          e.preventDefault();
          // This will be handled by parent component
        }
        return;
      }

      switch (e.key) {
        case 'Escape':
          onClose();
          break;
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1));
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
          break;
        case 'Enter':
          e.preventDefault();
          if (results[selectedIndex]) {
            handleResultClick(results[selectedIndex]);
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, results, selectedIndex, onClose]);

  const handleResultClick = (result) => {
    const typeRoutes = {
      task: `/tasks`,
      user: `/users`,
      group: `/organization`,
      inspection: `/inspections`,
      checklist: `/checklists`,
      workflow: `/workflows`
    };

    const route = typeRoutes[result.type];
    if (route) {
      navigate(route);
      onClose();
    }
  };

  const getResultIcon = (type) => {
    const iconClass = "w-5 h-5";
    switch (type) {
      case 'task':
        return <CheckSquare className={`${iconClass} text-blue-500`} />;
      case 'user':
        return <Users className={`${iconClass} text-purple-500`} />;
      case 'group':
        return <Folder className={`${iconClass} text-yellow-500`} />;
      case 'inspection':
        return <FileText className={`${iconClass} text-green-500`} />;
      case 'checklist':
        return <CheckSquare className={`${iconClass} text-orange-500`} />;
      case 'workflow':
        return <Clock className={`${iconClass} text-pink-500`} />;
      default:
        return <FileText className={`${iconClass} text-gray-500`} />;
    }
  };

  const getResultTypeBadge = (type) => {
    const colors = {
      task: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      user: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
      group: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
      inspection: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      checklist: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
      workflow: 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300'
    };

    return colors[type] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-start justify-center pt-[15vh]"
      onClick={onClose}
    >
      <div 
        className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl w-full max-w-2xl mx-4 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <Search className="w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for tasks, users, groups, inspections..."
            className="flex-1 bg-transparent border-none outline-none text-gray-900 dark:text-white placeholder-gray-400 text-base"
            autoFocus
          />
          <div className="flex items-center gap-2">
            <kbd className="hidden sm:inline-block px-2 py-1 text-xs font-mono bg-gray-100 dark:bg-gray-700 rounded border border-gray-300 dark:border-gray-600">
              ESC
            </kbd>
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Search Results */}
        <div className="max-h-[60vh] overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3"></div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Searching...</p>
            </div>
          ) : query.length < 2 ? (
            <div className="p-8 text-center">
              <Search className="w-12 h-12 text-gray-300 dark:text-gray-700 mx-auto mb-3" />
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Start typing to search...
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-600 mt-1">
                Search for tasks, users, groups, and more
              </p>
            </div>
          ) : results.length === 0 ? (
            <div className="p-8 text-center">
              <Search className="w-12 h-12 text-gray-300 dark:text-gray-700 mx-auto mb-3" />
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No results found for "{query}"
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-600 mt-1">
                Try a different search term
              </p>
            </div>
          ) : (
            <div className="py-2">
              {/* Group results by type */}
              {Object.entries(
                results.reduce((acc, result) => {
                  if (!acc[result.type]) acc[result.type] = [];
                  acc[result.type].push(result);
                  return acc;
                }, {})
              ).map(([type, typeResults]) => (
                <div key={type} className="mb-2">
                  <div className="px-4 py-2">
                    <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      {type}s ({typeResults.length})
                    </h3>
                  </div>
                  {typeResults.map((result, index) => {
                    const globalIndex = results.indexOf(result);
                    return (
                      <button
                        key={result.id}
                        onClick={() => handleResultClick(result)}
                        className={`w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors ${
                          globalIndex === selectedIndex
                            ? 'bg-gray-100 dark:bg-gray-700'
                            : ''
                        }`}
                      >
                        <div>{getResultIcon(result.type)}</div>
                        <div className="flex-1 text-left min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                              {result.title}
                            </p>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${getResultTypeBadge(result.type)}`}>
                              {result.type}
                            </span>
                          </div>
                          {result.description && (
                            <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-1">
                              {result.description}
                            </p>
                          )}
                          {result.metadata && (
                            <div className="flex items-center gap-2 mt-1">
                              {result.metadata.status && (
                                <span className="text-xs text-gray-400 dark:text-gray-600">
                                  Status: {result.metadata.status}
                                </span>
                              )}
                              {result.metadata.priority && (
                                <span className="text-xs text-gray-400 dark:text-gray-600">
                                  Priority: {result.metadata.priority}
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                        <kbd className="hidden sm:inline-block px-2 py-1 text-xs font-mono bg-gray-100 dark:bg-gray-700 rounded border border-gray-300 dark:border-gray-600">
                          ↵
                        </kbd>
                      </button>
                    );
                  })}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer with keyboard shortcuts */}
        <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-2 bg-gray-50 dark:bg-gray-900/50">
          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600">↑</kbd>
                <kbd className="px-1.5 py-0.5 bg-white dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600">↓</kbd>
                Navigate
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600">↵</kbd>
                Select
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600">ESC</kbd>
                Close
              </span>
            </div>
            <span>Global Search</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GlobalSearch;
