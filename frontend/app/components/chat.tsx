'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Paperclip, X, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';

export function ChatComponent() {
    const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([
        { role: 'assistant', content: "Hello! I'm your **UtilMaster Assistant**. I can help you with PPTs, PDFs, and more. ✨" }
    ]);
    const [input, setInput] = useState('');
    const [attachment, setAttachment] = useState<{ name: string; path: string } | null>(null);
    const [uploading, setUploading] = useState(false);
    const [sending, setSending] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setUploading(true);

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('http://localhost:8000/upload', {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) throw new Error('Upload failed');

                const data = await response.json();
                setAttachment({ name: data.filename, path: data.filepath });
            } catch (error) {
                console.error('Upload error:', error);
                alert('Failed to upload file.');
            } finally {
                setUploading(false);
                if (fileInputRef.current) fileInputRef.current.value = '';
            }
        }
    };

    const handleSend = async () => {
        if (!input.trim() && !attachment) return;

        const messageContent = input;
        let finalContent = messageContent;

        if (attachment) {
            finalContent += ` [Attached: ${attachment.path}]`;
        }

        const displayContent = input.trim() || `Check the attached file${attachment ? ': ' + attachment.name : ''}`;
        setMessages(prev => [...prev, { role: 'user', content: displayContent }]);
        setInput('');
        setSending(true);

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: finalContent })
            });
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error connecting to the server." }]);
        } finally {
            setAttachment(null);
            setSending(false);
        }
    };

    return (
        <div className="relative h-screen w-full overflow-hidden bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
            {/* Animated background effects */}
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDMpIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-20" />

            {/* Main container with glassmorphism */}
            <div className="relative h-full flex flex-col items-center justify-center p-4">
                <div className="w-full max-w-4xl h-[85vh] flex flex-col backdrop-blur-xl bg-white/5 rounded-3xl border border-white/10 shadow-2xl overflow-hidden">
                    {/* Header */}
                    <div className="px-6 py-4 border-b border-white/10 bg-gradient-to-r from-purple-500/10 to-blue-500/10">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 shadow-lg shadow-purple-500/50">
                                <Sparkles className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                                    UtilMaster
                                </h1>
                                <p className="text-xs text-gray-400">AI-Powered Utility Assistant</p>
                            </div>
                        </div>
                    </div>

                    {/* Messages area */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={cn(
                                    "flex items-start gap-3 animate-in slide-in-from-bottom-2 duration-300",
                                    msg.role === 'user' ? "flex-row-reverse" : "flex-row"
                                )}
                            >
                                {/* Avatar */}
                                <div className={cn(
                                    "w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-lg",
                                    msg.role === 'user'
                                        ? "bg-gradient-to-br from-blue-500 to-purple-500"
                                        : "bg-gradient-to-br from-purple-500 to-pink-500"
                                )}>
                                    {msg.role === 'user' ? <User size={18} className="text-white" /> : <Bot size={18} className="text-white" />}
                                </div>

                                {/* Message bubble */}
                                <div className={cn(
                                    "rounded-2xl px-4 py-3 max-w-[80%] backdrop-blur-sm shadow-lg transition-all hover:shadow-xl",
                                    msg.role === 'user'
                                        ? "bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30"
                                        : "bg-white/5 border border-white/10"
                                )}>
                                    <ReactMarkdown
                                        components={{
                                            a: ({ node, ...props }) => (
                                                <a
                                                    {...props}
                                                    className="underline font-semibold text-blue-400 hover:text-blue-300 transition-colors cursor-pointer"
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                />
                                            ),
                                            p: ({ node, ...props }) => <p {...props} className="text-gray-100 leading-relaxed" />,
                                            strong: ({ node, ...props }) => <strong {...props} className="text-white font-semibold" />,
                                            code: ({ node, ...props }) => <code {...props} className="px-1.5 py-0.5 rounded bg-white/10 text-purple-300 text-sm font-mono" />
                                        }}
                                    >
                                        {msg.content}
                                    </ReactMarkdown>
                                </div>
                            </div>
                        ))}
                        {sending && (
                            <div className="flex items-start gap-3">
                                <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg animate-pulse">
                                    <Bot size={18} className="text-white" />
                                </div>
                                <div className="rounded-2xl px-4 py-3 bg-white/5 border border-white/10">
                                    <div className="flex gap-1.5">
                                        <div className="w-2 h-2 rounded-full bg-purple-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <div className="w-2 h-2 rounded-full bg-pink-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input area */}
                    <div className="p-4 border-t border-white/10 bg-white/5 backdrop-blur-sm">
                        {attachment && (
                            <div className="mb-3 flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-500/20 border border-purple-500/30 backdrop-blur-sm">
                                <Paperclip size={16} className="text-purple-400" />
                                <span className="text-sm text-gray-300 flex-1 truncate">{attachment.name}</span>
                                <button
                                    onClick={() => setAttachment(null)}
                                    className="p-1 hover:bg-white/10 rounded-lg transition-colors"
                                >
                                    <X size={16} className="text-gray-400" />
                                </button>
                            </div>
                        )}

                        <div className="flex items-end gap-2">
                            <input
                                type="file"
                                ref={fileInputRef}
                                onChange={handleFileSelect}
                                className="hidden"
                            />
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                disabled={uploading}
                                className="p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
                            >
                                {uploading ? (
                                    <div className="w-5 h-5 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
                                ) : (
                                    <Paperclip size={20} className="text-gray-400" />
                                )}
                            </button>

                            <div className="flex-1 relative">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                                    placeholder="Type your message..."
                                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-purple-500/50 focus:bg-white/10 transition-all backdrop-blur-sm"
                                    disabled={sending}
                                />
                            </div>

                            <button
                                onClick={handleSend}
                                disabled={(!input.trim() && !attachment) || sending}
                                className="p-3 rounded-xl bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-105 disabled:hover:scale-100 shadow-lg shadow-purple-500/50"
                            >
                                <Send size={20} className="text-white" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
