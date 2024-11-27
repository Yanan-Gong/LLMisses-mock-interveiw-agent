import React from 'react';
import { MessageCircleQuestion, Users, Megaphone } from 'lucide-react';
import { Link } from 'react-router-dom'
import '../App.css';

const LandingPage = () => {
  return (
    <div className="landing-page-background">
      {/* Navigation */}
      <nav className="flex items-center justify-between p-4">
        <div className="header">AI Mock Interview</div>
        <div className="flex items-center gap-6">
          <button  className="button">Home</button>
          <button  className="button">About</button>
          <button  className="button">Services</button>
          <button className="button">
            Log In
          </button>
          <button className="button">
            Sign Up
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="text-center px-4 pt-20 pb-12">
        <h2 className="hero-title">
          Practice, Perfect, Perform:
        </h2>
        <h1 className="hero">
          Your Interview Rehearsal, Anytime, Anywhere
        </h1>
        <p className="hero-text">
          Customize Your Interview Simulations, Receive Instant, Insightful Feedback To
          Refine Your Answers, Build Confidence To Ace Your Next Interview!
        </p>
        <div className="flex justify-center">
          <Link to="/chat-interface">
            <button className="button">
              GET STARTED
            </button>
          </Link>
        </div>
      </main>

      {/* Features Section */}
      <section className="px-4 py-16">
        <h2 className="text-white text-3xl font-bold text-center mb-12">
          Explore Mock Interview AI
        </h2>
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Feature Card 1 */}
          <div className="bg-blue-900/50 p-6 rounded-lg backdrop-blur-sm">
            <div className="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center mb-4">
              <MessageCircleQuestion className="text-white w-6 h-6" />
            </div>
            <h3 className="text-white text-xl font-semibold mb-2">
              Customized Question
            </h3>
            <p className="text-blue-200">
              Get customized interview questions based on your roles and your
              experiences.
            </p>
          </div>

          {/* Feature Card 2 */}
          <div className="bg-blue-900/50 p-6 rounded-lg backdrop-blur-sm">
            <div className="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center mb-4">
              <Users className="text-white w-6 h-6" />
            </div>
            <h3 className="text-white text-xl font-semibold mb-2">
              Insightful Feedback
            </h3>
            <p className="text-blue-200">
              Enhance your interview prep with insightful and instant feedback
              powered by AI
            </p>
          </div>

          {/* Feature Card 3 */}
          <div className="bg-blue-900/50 p-6 rounded-lg backdrop-blur-sm">
            <div className="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center mb-4">
              <Megaphone className="text-white w-6 h-6" />
            </div>
            <h3 className="text-white text-xl font-semibold mb-2">
              Interview Community
            </h3>
            <p className="text-blue-200">
              Elevate resources from community and peer to better prepare your
              interviews
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
