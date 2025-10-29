import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import { getAIMessage } from "../api/api";
import { marked } from "marked";

function ChatWindow() {
  // Default message to show when chat loads
  const defaultMessage = [
    {
      role: "assistant",
      content: "Hi, how can I help you today?",
    },
  ];

  // State for messages and input
  const [messages, setMessages] = useState(defaultMessage);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false); // Show loading state while waiting for backend

  // Reference to scroll to bottom of messages
  const messagesEndRef = useRef(null);

  /**
   * Scroll to bottom of messages
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  /**
   * Scroll when messages update
   */
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * Handle Send Message
   * Fixed: Now uses state directly instead of parameter
   */
  const handleSend = async () => {
    // Get the current input value from state
    const userMessage = input.trim();

    // Validate: message must not be empty
    if (userMessage === "") {
      return; // Don't send empty messages
    }

    try {
      // 1. Add user message to chat
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: "user", content: userMessage },
      ]);

      // 2. Clear input field
      setInput("");

      // 3. Show loading state
      setIsLoading(true);

      // 4. Call backend API and get response
      const assistantMessage = await getAIMessage(userMessage);

      // 5. Add assistant message to chat
      setMessages((prevMessages) => [...prevMessages, assistantMessage]);
    } catch (error) {
      // Handle any errors
      console.error("Error in handleSend:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      // 6. Hide loading state
      setIsLoading(false);
    }
  };

  /**
   * Handle Key Press
   * Send message on Enter key (not Shift+Enter)
   */
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey && !isLoading) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="messages-container">
      {/* Display all messages */}
      {messages.map((message, index) => (
        <div key={index} className={`${message.role}-message-container`}>
          {message.content && (
            <div className={`message ${message.role}-message`}>
              {/* Parse markdown and display content */}
              <div
                dangerouslySetInnerHTML={{
                  __html: marked(message.content).replace(/<p>|<\/p>/g, ""),
                }}
              ></div>
            </div>
          )}
        </div>
      ))}

      {/* Show loading indicator while waiting for response */}
      {isLoading && (
        <div className="assistant-message-container">
          <div className="message assistant-message">
            <div>⏳ Loading response from backend...</div>
          </div>
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />

      {/* Input area */}
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          rows="3"
          disabled={isLoading} // Disable input while loading
        />
        <button
          className="send-button"
          onClick={handleSend}
          disabled={isLoading || input.trim() === ""} // Disable button while loading or empty
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;