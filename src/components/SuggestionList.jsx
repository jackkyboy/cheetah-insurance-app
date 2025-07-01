import React from "react";

const suggestions = [
  {
    text: "อยากรู้ว่าประกันภัยรถยนต์แบบไหนเหมาะกับมือใหม่",
    icon: "directions_car",
  },
  {
    text: "ประกันชั้น 1 กับ 2+ ต่างกันยังไง?",
    icon: "help",
  },
  {
    text: "ต้องทำยังไงเมื่อเกิดอุบัติเหตุบนถนน",
    icon: "report",
  },
  {
    text: "มีแนะนำบริษัทประกันที่เคลมเร็วไหม?",
    icon: "speed",
  },
];

const SuggestionList = ({ onSelect }) => {
  return (
    <ul className="suggestion-list">
      {suggestions.map((item, index) => (
        <li
          key={index}
          className="suggestion"
          onClick={() => onSelect(item.text)}
        >
          <h4 className="text">{item.text}</h4>
          <span className="icon material-symbols-rounded">{item.icon}</span>
        </li>
      ))}
    </ul>
  );
};

export default SuggestionList;
