// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/Home.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import StepForm from "../components/StepForm";
import Header from "../components/Header"; // Shared Header
import Footer from "../components/Footer"; // Shared Footer
import { useAuth } from "../context/AuthContext";
import { getInsuranceReviewSummary } from "../api/reviewService";
import "../assets/styles/Home.css";


const Home = () => {
  const navigate = useNavigate();
  const { authToken, logout } = useAuth();
  const [reviewSummary, setReviewSummary] = useState([]);
  const [loadingReviews, setLoadingReviews] = useState(true);
  const [reviewError, setReviewError] = useState("");

  useEffect(() => {
    let isMounted = true;

    const fetchReviewSummary = async () => {
      try {
        const summary = await getInsuranceReviewSummary();
        if (isMounted) {
          setReviewSummary(Array.isArray(summary) ? summary : []);
        }
      } catch (err) {
        if (isMounted) {
          setReviewError("ไม่สามารถโหลดข้อมูลรีวิวได้");
        }
      } finally {
        if (isMounted) {
          setLoadingReviews(false);
        }
      }
    };

    if (authToken) {
      fetchReviewSummary();
    }

    return () => {
      isMounted = false;
    };
  }, [authToken]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="home">
      <Header />
      <main className="home-main">
        <div className="home-form-container">
          <h2 className="form-title">กรอกข้อมูลรถยนต์ของคุณ</h2>
          <StepForm />
        </div>

        <div className="insurance-review-summary">
          <h2>คะแนนเฉลี่ยของบริษัทประกันภัย</h2>
          {loadingReviews ? (
            <p>กำลังโหลดข้อมูล...</p>
          ) : reviewError ? (
            <p>{reviewError}</p>
          ) : (
            <table className="review-summary-table">
              <thead>
                <tr>
                  <th>บริษัทประกันภัย</th>
                  <th>คะแนนเฉลี่ย</th>
                  <th>จำนวนรีวิว</th>
                </tr>
              </thead>
              <tbody>
                {reviewSummary.map((item) => (
                  <tr key={item.company_id}>
                    <td>{getCompanyName(item.company_id)}</td>
                    <td>{item.average_rating ? item.average_rating.toFixed(2) : "N/A"} ⭐</td>
                    <td>{item.review_count || "N/A"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
};

// Map company_id to company name
const getCompanyName = (company_id) => {
  const companies = {
    1: "บริษัท เอ็ม เอส ไอ จี",
    2: "บริษัท กรุงไทยพานิชประกันภัย",
    3: "บริษัท ทิพยประกันภัย",
    4: "บริษัท แอกซ่าประกันภัย",
    5: "บริษัท กรุงเทพประกันภัย",
    6: "บริษัท วิริยะประกันภัย",
    7: "บริษัท ฟอลคอนประกันภัย",
    8: "บริษัท คุ้มภัยโตเกียวมารีน",
    9: "บริษัท ชับบ์สามัคคี",
    10: "บริษัท เมืองไทยประกันภัย",
  };
  return companies[company_id] || "บริษัทไม่ทราบชื่อ";
};

export default Home;
