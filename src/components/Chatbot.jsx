import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { Button, Card, Form, Container } from "react-bootstrap";
import "../assets/styles/chatbot.css"; // ✅ นำเข้า CSS

const Chatbot = ({ floating = true }) => {
  const [open, setOpen] = useState(!floating);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const toggleChat = () => setOpen(!open);

  const sendMessage = () => {
    if (input.trim() !== "") {
      setMessages([...messages, { text: input, sender: "user" }]);
      setInput("");

      // ✅ Simulate bot response
      setTimeout(() => {
        setMessages((prev) => [...prev, { text: "นี่คือคำตอบจากบอท!", sender: "bot" }]);
      }, 1000);
    }
  };

  return (
    <div id="chatbot-container">
      {/* ✅ Floating Chat Toggle */}
      {floating && (
        <Button variant="primary" id="chatbot-toggle" onClick={toggleChat}>
          💬
        </Button>
      )}

      {/* ✅ Chatbox UI */}
      {open && (
        <Container id="chatbot-box">
          <Card className="chatbot-card shadow-lg">
            {/* ✅ Chatbot Header */}
            <Card.Header className="chatbot-header">
              <span>💬 Chatbot</span>
              {floating && (
                <Button variant="danger" size="sm" className="chatbot-close-btn" onClick={toggleChat}>
                  ✖
                </Button>
              )}
            </Card.Header>

            {/* ✅ Chatbox Messages */}
            <Card.Body className="chatbot-body">
              <div className="chatbox">
                {messages.map((msg, index) => (
                  <div key={index} className={`message ${msg.sender}`}>
                    {msg.text}
                  </div>
                ))}
              </div>

              {/* ✅ Input Field + Send Button */}
              <Form className="chatbox-input">
                <Form.Control
                  type="text"
                  placeholder="พิมพ์ข้อความ..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="chatbox-input-field"
                />
                <Button variant="primary" onClick={sendMessage} className="chatbox-send-btn">
                  🚀
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Container>
      )}
    </div>
  );
};

export default Chatbot;
