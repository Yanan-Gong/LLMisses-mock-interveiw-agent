import React, { useState } from 'react';
import { MessageCircleQuestion, Paperclip, Send, Mic } from 'lucide-react';
import axios from 'axios';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      content: "Before we start today's interview rehearsal, I have couple of questions for you. What position are you preparing for? Please type in the job description."
    }
    // ,
    // {
    //   type: 'user',
    //   content: "Seeking A Data Scientist For Pricing Optimization Analytics Team Who Is Enthusiastic About Problem-Solving, Adept At Generating Valuable Insights From Data Through Deep Dive Analysis... A Successful Candidate Will Have At Least 4+ Years Of Experience Analyzing Large, Multi-Dimensional Data Sets And Synthesizing Insights Into Actionable Solution... Fluent In SQL And Scripting Languages Such As Python Or R, Comfortable Working With Large, Complex, And Potentially Messy Datasets..."
    // },
    // {
    //   type: 'bot',
    //   content: "Awesome! Then could you upload your resume as an attachment? Both PDF or Docx formats work for me."
    // },
    // {
    //   type: 'user',
    //   file: {
    //     name: "Ashley Resume - DS Analytics - 20240101.Pdf",
    //     type: "pdf"
    //   }
    // }
  ]);
  const [inputMessage, setInputMessage] = useState('');

  const handleSendMessage = async () => {
    if (inputMessage.trim()) {
      setMessages([...messages, { type: 'user', content: inputMessage }]);
      try {
        const response = await axios.post("http://localhost:5173/", {
          question: inputMessage,
        });
        setMessages([...messages, { type: 'bot', content: response.data.answer }]);
    }
    catch (error) {
      //     setMessages((prev) => [
      //       ...prev,
      //       { sender: "bot", text: "Sorry, something went wrong!" },
      //     ]);
      setMessages([...messages, { type: 'bot', content: "Sorry, something went wrong!" }]);
    }
      setInputMessage('');
  };
}


  // const handleSend = async () => {
  //   if (!userMessage.trim()) return;

  //   // Add user's message to the chat
  //   setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);

  //   try {
  //     const response = await axios.post("http://127.0.0.1:5000/chat", {
  //       question: userMessage,
  //     });

  //     // Add bot's response to the chat
  //     setMessages((prev) => [...prev, { sender: "bot", text: response.data.answer }]);
  //   } catch (error) {
  //     setMessages((prev) => [
  //       ...prev,
  //       { sender: "bot", text: "Sorry, something went wrong!" },
  //     ]);
  //   }

  //   setUserMessage("");
  // };


  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setMessages([...messages, { 
        type: 'user', 
        file: {
          name: file.name,
          type: file.type
        }
      }]);
    }
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
        <h1 className="text-white text-2xl font-bold mb-6">Good morning, Ashley!</h1>
        
        {/* Messages Area */}
        <div className="space-y-4 mb-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'items-start'}`}>
              {message.type === 'bot' && (
                <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center mr-3">
                  <MessageCircleQuestion className="text-white w-6 h-6" />
                </div>
              )}
              
              <div className={`max-w-2xl rounded-lg p-4 ${
                message.type === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-blue-900/50 backdrop-blur-sm text-white'
              }`}>
                {message.content && <p>{message.content}</p>}
                {message.file && (
                  <div className="flex items-center gap-2 text-white">
                    <div className="bg-red-500 p-2 rounded">
                      <span className="text-sm">PDF</span>
                    </div>
                    <span>{message.file.name}</span>
                  </div>
                )}
              </div>

              {message.type === 'user' && (
                <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center ml-3">
                  <div className="text-white">A</div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input Area */}
        <div className="bg-blue-900/30 rounded-lg p-2 backdrop-blur-sm">
          <div className="flex items-center gap-2">
            <label className="cursor-pointer">
              <input 
                type="file" 
                className="hidden" 
                onChange={handleFileUpload}
                accept=".pdf,.docx"
              />
              <Paperclip className="text-white w-6 h-6" />
            </label>
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Message Chatbot.."
              className="flex-1 bg-transparent text-white placeholder-blue-300 outline-none"
            />
            <button className="p-2">
              <Mic className="text-white w-6 h-6" />
            </button>
            <button 
              onClick={handleSendMessage}
              className="bg-white rounded-full p-2"
            >
              <Send className="text-blue-900 w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
