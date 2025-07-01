// /Users/apichet/Downloads/cheetah-insurance-app/src/components/ChatInput.jsx
import React, { useState } from "react";
import { fetchGalleryPackages } from "../api/gallery";
import { parseInsuranceQuery } from "../utils/nlp";
import { askOllama } from "../api/ollamaService";

const ChatInput = ({ onSend, onBotResponse }) => {
  const [input, setInput] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const userText = input.trim();
    if (!userText) return;

    onSend?.({ sender: "user", text: userText });
    setInput("");

    try {
      const query = parseInsuranceQuery(userText);
      const isComplete = query.brand && query.model && query.year && query.insurance_type;

      if (isComplete) {
        onBotResponse?.({
          sender: "bot",
          text: "🔎 กำลังค้นหาข้อมูลจริงจากระบบ...",
        });

        const results = await fetchGalleryPackages(query);

        if (results.length > 0) {
          onBotResponse?.({
            sender: "bot",
            text: `✅ พบแพ็กเกจ ${results.length} รายการที่ตรงกับคำค้นของคุณ 👇`,
            packages: results,
          });
        } else {
          onBotResponse?.({
            sender: "bot",
            text: "❌ ไม่พบข้อมูลในระบบจริง ลองเปลี่ยนรุ่น/ปี หรือประเภทประกันดูครับ 🙏",
          });
        }

        return; // 🛑 ห้าม fallback ไป Ollama เด็ดขาด
      }

      // 🧠 คำถามความรู้ทั่วไป เช่น “ต่างกันยังไง”
      const reply = await askOllama(userText);
      onBotResponse?.({
        sender: "bot",
        text: reply || "⚠️ ขออภัย ระบบไม่สามารถตอบคำถามได้ในตอนนี้",
      });

    } catch (err) {
      console.error("❌ Error in ChatInput:", err);
      onBotResponse?.({
        sender: "bot",
        text: "เกิดข้อผิดพลาดในการประมวลผล กรุณาลองใหม่อีกครั้งครับ 😓",
      });
    }
  };

  return (
    <form className="typing-form" onSubmit={handleSubmit}>
      <div className="input-wrapper">
        <input
          type="text"
          className="typing-input"
          placeholder="พิมพ์ข้อความที่นี่..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          required
        />
        <button className="icon material-symbols-rounded" type="submit">
          send
        </button>
      </div>
    </form>
  );
};

export default ChatInput;
