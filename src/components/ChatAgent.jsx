// /Users/apichet/Downloads/cheetah-insurance-app/src/components/ChatAgent.jsx
import React, { useState, useEffect, useRef } from "react";
import "../assets/styles/chatagent.css";
import MessageBubble from "./MessageBubble";
import SuggestionList from "./SuggestionList";
import ChatInput from "./ChatInput";

import {
  askOllama,
  parseOllamaToPackages,
  detectFabricatedPremium,
} from "../api/ollamaService";
import { fetchPackagesWithLogos as fetchGalleryPackages } from "../api/api";
import { parseInsuranceQuery } from "../utils/nlp";


const ChatAgent = () => {
  const [messages, setMessages] = useState([]);
  const [theme, setTheme] = useState("light");
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleThemeToggle = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    document.body.classList.toggle("light_mode", newTheme === "light");
    setTheme(newTheme);
  };

  const handleUserSend = async (msg) => {
    setMessages((prev) => [...prev, msg]);
  
    // 🧠 1. ขอข้อมูลจาก Ollama ก่อน
    const ollamaText = await askOllama(msg.text);
    const parsedPackages = parseOllamaToPackages(ollamaText);
    const hasFake = parsedPackages.some((p) => p.flagged_fake_price);
  
    // 🧠 2. ตอบกลับจาก AI
    setMessages((prev) => [
      ...prev,
      {
        sender: "bot",
        text: hasFake
          ? "Ollama ตอบกลับพร้อมเบี้ยที่อาจไม่ยืนยันจากระบบจริง — กำลังดึงข้อมูลจริงให้ครับ"
          : "Ollama ตอบกลับเรียบร้อย — กำลังดึงข้อมูลจริงเพื่อยืนยัน",
        packages: parsedPackages,
      },
    ]);
  
    // ✅ 3. แยก intent แล้วดึงข้อมูลจากระบบจริง
    const parsedIntent = parseInsuranceQuery(msg.text);
  
    // 🛡️ ตรวจว่าข้อมูลพอไหมก่อนยิง API
    if (!parsedIntent.brand || !parsedIntent.model || !parsedIntent.year || !parsedIntent.insurance_type) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "⚠️ ข้อมูลที่ระบุยังไม่ครบ เช่น ยี่ห้อ รุ่น ปี หรือประเภทประกัน ลองพิมพ์ใหม่อีกครั้งครับ",
        },
      ]);
      return;
    }
  
    try {
      const realPackages = await fetchGalleryPackages({
        brand: parsedIntent.brand,
        model: parsedIntent.model,
        year: parsedIntent.year,
        type: parsedIntent.insurance_type,
        limit: 3,
        offset: 0,
      });
  
      if (Array.isArray(realPackages) && realPackages.length > 0) {
        setMessages((prev) => [
          ...prev,
          {
            sender: "bot",
            text: "✅ ข้อมูลจากระบบจริง:",
            packages: realPackages,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            sender: "bot",
            text: "❌ ไม่พบข้อมูลจากระบบจริงสำหรับคำขอนี้ครับ",
          },
        ]);
      }
    } catch (err) {
      console.error("🔥 fetchGalleryPackages error", err);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "⚠️ เกิดข้อผิดพลาดในการดึงข้อมูลจากระบบจริง",
        },
      ]);
    }
  };
  
  

  return (
    <div className="chat-container">
      {/* ✅ Header */}
      <header className="header">
        <h1 className="title">พี่เสือชีต้าพร้อมช่วยเหลือ</h1>
        <p className="subtitle">สอบถามเรื่องประกันได้เลยทันที</p>
        <SuggestionList
          onSelect={(msg) => handleUserSend({ sender: "user", text: msg })}
        />
      </header>

      {/* ✅ Chat Body */}
      <div className="chat-list">
        {messages.map((msg, index) => (
          <MessageBubble
            key={index}
            sender={msg.sender}
            text={msg.text}
            packages={msg.packages}
          />
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* ✅ Chat Input */}
      <ChatInput onSend={handleUserSend} />

      {/* ✅ Footer Actions */}
      <div className="chat-actions">
        <span className="icon material-symbols-rounded" onClick={handleThemeToggle}>
          {theme === "light" ? "dark_mode" : "light_mode"}
        </span>
        <span className="icon material-symbols-rounded" onClick={() => setMessages([])}>
          delete
        </span>
        <p className="disclaimer-text">
          พี่เสือชีต้าอาจแนะนำไม่แม่นยำ 100% โปรดใช้วิจารณญาณในการตัดสินใจ
        </p>
      </div>
    </div>
  );
};

export default ChatAgent;
