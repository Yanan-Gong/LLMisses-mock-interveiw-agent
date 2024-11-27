import React, { useState, useRef, useEffect } from 'react';
import { MessageCircleQuestion, Paperclip, Send, Mic, Play, Pause } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AudioMessage = ({ isBot, duration = "0:00" }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
    // Here you would implement actual audio playback
  };

  return (
    <div className="flex items-center gap-3">
      <button 
        onClick={togglePlay}
        className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center"
      >
        {isPlaying ? 
          <Pause className="w-4 h-4 text-white" /> : 
          <Play className="w-4 h-4 text-white" />
        }
      </button>
      <div className="flex-1 h-1 bg-white/20 rounded-full overflow-hidden">
        <div 
          className="h-full bg-blue-400 rounded-full"
          style={{ width: `${progress}%` }}
        />
      </div>
      <span className="text-sm text-white/80">{duration}</span>
      {!isBot && (
        <button className="text-blue-400 text-sm hover:underline">
          Convert to text
        </button>
      )}
    </div>
  );
};

const AudioChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "Interview begins :)",
      audio: true
    },
    {
      id: 2,
      type: 'bot',
      content: "Could you briefly introduce your background and experience? What motivates you for a new opportunity?",
      audio: true
    }
  ]);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const recordingInterval = useRef(null);

  useEffect(() => {
    if (isRecording) {
      recordingInterval.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      clearInterval(recordingInterval.current);
      setRecordingTime(0);
    }
    return () => clearInterval(recordingInterval.current);
  }, [isRecording]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}"`;
  };

  const startRecording = () => {
    setIsRecording(true);
    // Here you would implement actual audio recording
  };

  const stopRecording = () => {
    setIsRecording(false);
    // Here you would implement stopping the recording and sending the audio
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'user',
      audio: true,
      duration: formatTime(recordingTime)
    }]);
  };

  const handleNextQuestion = () => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'bot',
      content: "Could you tell me about a complex problem you solved at work? What was your approach to finding a solution?",
      audio: true
    }]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-blue-800">
      {/* Navigation */}
      <nav className="flex items-center justify-between p-4">
        <div className="text-white text-2xl font-bold">AI Mock Interview</div>
        <div className="flex items-center gap-6">
          <a href="#" className="text-blue-300 hover:text-blue-100">Home</a>
          <a href="#" className="text-blue-300 hover:text-blue-100">About</a>
          <a href="#" className="text-blue-300 hover:text-blue-100">Services</a>
          <button className="px-4 py-2 bg-blue-500 text-white rounded">
            Hi, Ashley!
          </button>
        </div>
      </nav>

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto p-4">
        {/* Messages Area */}
        <div className="space-y-6 mb-4 h-[70vh] overflow-y-auto">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'items-start'}`}
              >
                {message.type === 'bot' && (
                  <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center mr-3">
                    <MessageCircleQuestion className="text-white w-6 h-6" />
                  </div>
                )}
                
                <div className={`max-w-2xl rounded-lg p-4 ${
                  message.type === 'user' 
                    ? 'bg-blue-500 text-white ml-auto' 
                    : 'bg-blue-900/50 backdrop-blur-sm text-white'
                }`}>
                  {message.content && <p className="mb-3">{message.content}</p>}
                  {message.audio && (
                    <AudioMessage 
                      isBot={message.type === 'bot'} 
                      duration={message.duration}
                    />
                  )}
                </div>

                {message.type === 'user' && (
                  <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center ml-3">
                    <div className="text-white">A</div>
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Recording Input Area */}
        <motion.div 
          className="bg-blue-900/30 rounded-lg p-2 backdrop-blur-sm"
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
        >
          <div className="flex items-center gap-2">
            <motion.label className="cursor-pointer">
              <input type="file" className="hidden" accept="audio/*" />
              <Paperclip className="text-white w-6 h-6" />
            </motion.label>
            
            <div className="flex-1 flex items-center gap-2 bg-blue-800/50 rounded-full px-4 py-2">
              <Mic className={`w-5 h-5 ${isRecording ? 'text-red-500' : 'text-white'}`} />
              {isRecording ? (
                <span className="text-white">Recording... {formatTime(recordingTime)}</span>
              ) : (
                <span className="text-white/60">Start Recording...</span>
              )}
            </div>

            <motion.button
              className="bg-white rounded-full p-3"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={isRecording ? stopRecording : startRecording}
            >
              {isRecording ? (
                <Send className="text-blue-900 w-5 h-5" />
              ) : (
                <Mic className="text-blue-900 w-5 h-5" />
              )}
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default AudioChatInterface;
