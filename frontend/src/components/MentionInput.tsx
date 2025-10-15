import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { AtSign, X } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

// Types
interface User {
  id: string;
  name: string;
  email: string;
  [key: string]: any;
}

interface MentionInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

interface MentionTextProps {
  text: string;
}

const MentionInput: React.FC<MentionInputProps> = ({ value, onChange, placeholder = "Add a comment...", className = "" }) => {
  const [showSuggestions, setShowSuggestions] = useState<boolean>(false);
  const [suggestions, setSuggestions] = useState<User[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [cursorPosition, setCursorPosition] = useState<number>(0);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (searchQuery && showSuggestions) {
      fetchUserSuggestions(searchQuery);
    }
  }, [searchQuery]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent): void => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchUserSuggestions = async (query: string): Promise<void> => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.get<{ users: User[] }>(
        `${API_BASE_URL}/api/mentions/search?query=${encodeURIComponent(query)}`,
        { headers }
      );
      
      setSuggestions(response.data.users || []);
    } catch (err) {
      console.error('Error fetching user suggestions:', err);
      setSuggestions([]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    const newValue = e.target.value;
    const newCursorPosition = e.target.selectionStart;
    
    onChange(newValue);
    setCursorPosition(newCursorPosition);

    // Check if user is typing @ mention
    const textBeforeCursor = newValue.substring(0, newCursorPosition);
    const lastAtSymbol = textBeforeCursor.lastIndexOf('@');
    
    if (lastAtSymbol !== -1) {
      const textAfterAt = textBeforeCursor.substring(lastAtSymbol + 1);
      
      // Check if there's no space after @ (valid mention in progress)
      if (!textAfterAt.includes(' ') && textAfterAt.length >= 0) {
        setSearchQuery(textAfterAt);
        setShowSuggestions(true);
        setSelectedIndex(0);
      } else {
        setShowSuggestions(false);
      }
    } else {
      setShowSuggestions(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, suggestions.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
        break;
      case 'Enter':
        if (showSuggestions) {
          e.preventDefault();
          insertMention(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        break;
    }
  };

  const insertMention = (user: User): void => {
    const textBeforeCursor = value.substring(0, cursorPosition);
    const textAfterCursor = value.substring(cursorPosition);
    const lastAtSymbol = textBeforeCursor.lastIndexOf('@');
    
    // Replace @query with @username
    const newText = 
      textBeforeCursor.substring(0, lastAtSymbol) +
      `@${user.email.split('@')[0]} ` + // Use email prefix as username
      textAfterCursor;
    
    onChange(newText);
    setShowSuggestions(false);
    setSearchQuery('');
    
    // Refocus input
    setTimeout(() => {
      if (inputRef.current) {
        const newCursorPos = lastAtSymbol + user.email.split('@')[0].length + 2;
        inputRef.current.focus();
        inputRef.current.setSelectionRange(newCursorPos, newCursorPos);
      }
    }, 0);

    // Notify backend about the mention
    createMention(user.id);
  };

  const createMention = async (userId: string): Promise<void> => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.post(
        `${API_BASE_URL}/api/mentions`,
        { mentioned_user_id: userId },
        { headers }
      );
    } catch (err) {
      console.error('Error creating mention:', err);
    }
  };

  return (
    <div className="relative">
      <div className="relative">
        <textarea
          ref={inputRef}
          value={value}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={`w-full ${className}`}
          rows={3}
        />
        
        <div className="absolute bottom-2 right-2 text-xs text-gray-400 dark:text-gray-600 flex items-center gap-1">
          <AtSign className="w-3 h-3" />
          <span>Type @ to mention</span>
        </div>
      </div>

      {/* Mention Suggestions Dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-60 overflow-y-auto"
        >
          {suggestions.map((user, index) => (
            <div
              key={user.id}
              onClick={() => insertMention(user)}
              className={`px-4 py-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 ${
                index === selectedIndex ? 'bg-blue-50 dark:bg-blue-900/20' : ''
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                  {user.name?.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {user.name}
                  </p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    @{user.email.split('@')[0]}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Help Text */}
      {showSuggestions && suggestions.length === 0 && searchQuery && (
        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            No users found matching "@{searchQuery}"
          </p>
        </div>
      )}
    </div>
  );
};

export default MentionInput;

// Preview component to display text with highlighted mentions
export const MentionText: React.FC<MentionTextProps> = ({ text }) => {
  const renderHighlightedText = (text: string): (JSX.Element | null)[] | null => {
    if (!text) return null;
    
    // Match @mentions
    const mentionRegex = /@(\w+)/g;
    const parts: JSX.Element[] = [];
    let lastIndex = 0;
    let match;

    while ((match = mentionRegex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(
          <span key={`text-${lastIndex}`}>
            {text.substring(lastIndex, match.index)}
          </span>
        );
      }

      parts.push(
        <span
          key={`mention-${match.index}`}
          className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 px-1 rounded font-medium cursor-pointer hover:bg-blue-200 dark:hover:bg-blue-900/50"
          title={`Mentioned user: ${match[0]}`}
        >
          {match[0]}
        </span>
      );

      lastIndex = match.index + match[0].length;
    }

    if (lastIndex < text.length) {
      parts.push(
        <span key={`text-${lastIndex}`}>
          {text.substring(lastIndex)}
        </span>
      );
    }

    return parts;
  };

  return <div className="whitespace-pre-wrap">{renderHighlightedText(text)}</div>;
};
