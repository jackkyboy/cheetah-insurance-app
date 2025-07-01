// /Users/apichet/Downloads/cheetah-insurance-app/src/components/Header.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toggleTheme, getSavedTheme, THEMES } from "../utils/themeToggle";
import "../assets/styles/Header.css";
import FancyUnderline from "./FancyUnderline";

const Header = () => {
  const navigate = useNavigate();
  const [theme, setTheme] = useState(getSavedTheme());

  const handleToggle = () => {
    const next = toggleTheme();
    setTheme(next); // อัปเดต icon
  };

  useEffect(() => {
    setTheme(getSavedTheme());
  }, []);

  const NavItem = ({ to, children }) => (
    <div className="nav-item" onClick={() => navigate(to)}>
      <FancyUnderline>{children}</FancyUnderline>
    </div>
  );

  return (
    <header className="header">
      <div className="logo" onClick={() => navigate("/")}>
        Cheetah Broker
      </div>

      <nav className="nav-links">
        <NavItem to="/login">Login</NavItem>
        <NavItem to="/register">Register</NavItem>
        <NavItem to="/profile">Profile</NavItem>

        {/* ✅ ปุ่ม Toggle พร้อม icon ที่เปลี่ยน */}
        <button
          className="btn-toggle"
          onClick={handleToggle}
          title="Toggle Theme"
          aria-label="Toggle Theme"
        >
          {theme === THEMES.DARK ? "🌞" : "🌙"}
        </button>
      </nav>
    </header>
  );
};

export default Header;
