// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
import './App.css'
import InterviewLandingPage from './pages/interview-landing-page.tsx'
import ChatInterface from './pages/chat-interface.tsx'
import AudioChatInterface from './pages/audio-chat-interface.tsx'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
// import Navbar from './components/Navbar'
// import Home from './pages/Home'
// import Auth from './pages/Auth'
// import Settings from './pages/Settings'
// import Editor from './pages/Editor'
// import GuestRoute from './components/GuestRoute'
// import AuthRoute from './components/AuthRoute'

function App() {
  // const [count, setCount] = useState(0)

  return (
    <Router>
      <header>
        {/* <Navbar /> */}
      </header>
      <main>
        <Routes>
          <Route path="/" element={<InterviewLandingPage />} />
          {/* <GuestRoute path="/register" element={<Auth key="register" />} />
          <GuestRoute path="/login" element={<Auth key="login" />} />
          <AuthRoute path="/settings" element={<Settings />} />
          <AuthRoute path="/editor" element={<Editor />} /> */}
          {/* <Route path="/interview-landing-page" element={<InterviewLandingPage />} /> */}
          <Route path="/chat-interface" element={<ChatInterface />} />
          <Route path="/audio-chat-interface" element={<AudioChatInterface />} />
        </Routes>
      </main>
    </Router>
  )
}

export default App


// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'
// import { interview-landing-page, chat-interface, audio-chat-interface} from './pages'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <div className="App">
//             <p>Hello</p>
//         </div>
//   )
// }



// // function App() {
// //   function App() {
// //     return (
// //       <Router>
// //         <header>
// //           <Navbar />
// //         </header>
// //         <main>
// //           <Routes>
// //             <Route path="/" element={<Home />} />
// //             <GuestRoute path="/register" element={<Auth key="register" />} />
// //             <GuestRoute path="/login" element={<Auth key="login" />} />
// //             <AuthRoute path="/settings" element={<Settings />} />
// //             <AuthRoute path="/editor" element={<Editor />} />
// //             <Route path="/editor/:slug" element={<Editor />} />
// //             <Route path="/article/:slug" element={<Article />} />
// //             <Route path="/profile/:username" element={<Profile />} />
// //             <AuthRoute path="/@:username" element={<Profile />} />
// //           </Routes>
// //         </main>
// //         <footer>
// //           <div className="container">
// //             <Link to="/" className="logo-font">
// //               conduit
// //             </Link>
// //             <span className="attribution">
// //               An interactive learning project from <a href="https://thinkster.io">Thinkster</a>. Code &amp; design
// //               licensed under MIT.
// //             </span>
// //           </div>
// //         </footer>
// //       </Router>
// //     )
// //   }

// // }

// export default App
