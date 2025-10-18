// @ts-nocheck
import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { ModernPageWrapper } from '@/design-system/components';
import { Send, MessageCircle, Plus } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TeamChatPage = () => {
  const [channels, setChannels] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadChannels();
  }, []);

  useEffect(() => {
    if (selectedChannel) {
      loadMessages(selectedChannel.id);
    }
  }, [selectedChannel]);

  const loadChannels = async () => {
    try {
      const response = await axios.get(`${API}/chat/channels`);
      setChannels(response.data);
      if (response.data.length > 0 && !selectedChannel) {
        setSelectedChannel(response.data[0]);
      }
    } catch (err) {
      console.error('Failed to load channels:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (channelId) => {
    try {
      const response = await axios.get(`${API}/chat/channels/${channelId}/messages`);
      setMessages(response.data.reverse());
      scrollToBottom();
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedChannel) return;

    try {
      await axios.post(`${API}/chat/channels/${selectedChannel.id}/messages`, {
        content: newMessage,
      });
      setNewMessage('');
      loadMessages(selectedChannel.id);
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <ModernPageWrapper title="Team Chat" subtitle="Real-time team communication">
      <div className="grid grid-cols-12 gap-4 h-[calc(100vh-200px)]">
        <Card className="col-span-3">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="text-base">Channels</CardTitle>
              <Button size="sm" variant="outline">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[calc(100vh-300px)]">
              <div className="space-y-2">
                {channels.map((channel) => (
                  <div
                    key={channel.id}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedChannel?.id === channel.id
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-slate-100 dark:hover:bg-slate-800'
                    }`}
                    onClick={() => setSelectedChannel(channel)}
                  >
                    <div className="font-medium">{channel.name}</div>
                    <div className="text-xs opacity-75">{channel.member_ids.length} members</div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        <Card className="col-span-9 flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5" />
              {selectedChannel?.name || 'Select a channel'}
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col">
            <ScrollArea className="flex-1 pr-4 mb-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div key={message.id} className="flex gap-3">
                    <div className="flex-1">
                      <div className="flex items-baseline gap-2">
                        <span className="font-medium">{message.sender_name}</span>
                        <span className="text-xs text-muted-foreground">
                          {new Date(message.sent_at).toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="text-sm mt-1">{message.content}</div>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <Input
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type a message..."
                disabled={!selectedChannel}
              />
              <Button type="submit" disabled={!selectedChannel || !newMessage.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </ModernPageWrapper>
  );
};

export default TeamChatPage;
