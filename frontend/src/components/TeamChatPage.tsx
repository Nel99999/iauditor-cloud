// @ts-nocheck
import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ModernPageWrapper } from '@/design-system/components';
import { Send, MessageCircle, Plus, Video, Mic, MicOff, VideoOff, PhoneOff } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TeamChatPage = () => {
  const [channels, setChannels] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [showVideoCall, setShowVideoCall] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
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
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${selectedChannel?.id === channel.id
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
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <MessageCircle className="h-5 w-5" />
                {selectedChannel?.name || 'Select a channel'}
              </CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowVideoCall(true)}
                disabled={!selectedChannel}
              >
                <Video className="h-4 w-4 mr-2" />
                Start Video Call
              </Button>
            </div>
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

      {/* Video Call Dialog */}
      <Dialog open={showVideoCall} onOpenChange={setShowVideoCall}>
        <DialogContent className="max-w-4xl h-[600px] p-0">
          <div className="h-full flex flex-col bg-slate-900 rounded-lg overflow-hidden">
            <DialogHeader className="p-4 border-b border-slate-700">
              <DialogTitle className="text-white flex items-center gap-2">
                <Video className="h-5 w-5" />
                Video Call - {selectedChannel?.name}
              </DialogTitle>
            </DialogHeader>

            <div className="flex-1 relative bg-slate-800">
              {/* Main Video Area */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center text-white">
                  <div className="w-32 h-32 mx-auto mb-4 rounded-full bg-slate-700 flex items-center justify-center">
                    <Video className="h-16 w-16 text-slate-400" />
                  </div>
                  <p className="text-lg font-medium">Simulated Video Call</p>
                  <p className="text-sm text-slate-400 mt-2">This is a demo interface</p>
                  <p className="text-xs text-slate-500 mt-4">
                    In production, this would integrate with WebRTC or a service like Twilio/Agora
                  </p>
                </div>
              </div>

              {/* Self View (Picture-in-Picture) */}
              <div className="absolute bottom-4 right-4 w-48 h-36 bg-slate-700 rounded-lg border-2 border-slate-600 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-2 rounded-full bg-slate-600 flex items-center justify-center">
                    <Video className="h-8 w-8 text-slate-400" />
                  </div>
                  <p className="text-xs text-slate-400">You</p>
                </div>
              </div>

              {/* Participants Indicator */}
              <div className="absolute top-4 left-4">
                <Badge className="bg-slate-700/80 text-white border-slate-600">
                  {selectedChannel?.member_ids.length || 0} participants
                </Badge>
              </div>
            </div>

            {/* Video Controls */}
            <div className="p-6 bg-slate-900 border-t border-slate-700">
              <div className="flex items-center justify-center gap-4">
                <Button
                  variant="outline"
                  size="lg"
                  className={`rounded-full w-14 h-14 ${isMuted ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-slate-700 hover:bg-slate-600 text-white border-slate-600'}`}
                  onClick={() => setIsMuted(!isMuted)}
                >
                  {isMuted ? <MicOff className="h-6 w-6" /> : <Mic className="h-6 w-6" />}
                </Button>

                <Button
                  variant="outline"
                  size="lg"
                  className={`rounded-full w-14 h-14 ${isVideoOff ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-slate-700 hover:bg-slate-600 text-white border-slate-600'}`}
                  onClick={() => setIsVideoOff(!isVideoOff)}
                >
                  {isVideoOff ? <VideoOff className="h-6 w-6" /> : <Video className="h-6 w-6" />}
                </Button>

                <Button
                  variant="destructive"
                  size="lg"
                  className="rounded-full w-14 h-14"
                  onClick={() => setShowVideoCall(false)}
                >
                  <PhoneOff className="h-6 w-6" />
                </Button>
              </div>

              <div className="text-center mt-4">
                <p className="text-xs text-slate-400">
                  {isMuted && 'Microphone muted • '}
                  {isVideoOff && 'Camera off • '}
                  {!isMuted && !isVideoOff && 'Connected'}
                </p>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </ModernPageWrapper>
  );
};

export default TeamChatPage;
