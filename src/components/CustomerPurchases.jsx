import React, { useEffect, useState } from "react";
import "../assets/styles/CustomerPurchases.css";
import { fetchCustomerPurchases } from "../api/userService";

const CustomerPurchases = ({ customerId }) => {
  const [purchases, setPurchases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // โหลดข้อมูลการซื้อของลูกค้า
  const loadPurchases = async () => {
    try {
      setLoading(true);
      const purchasesData = await fetchCustomerPurchases(customerId);
      setPurchases(purchasesData || []);
    } catch (err) {
      console.error("❌ Error loading purchases:", err.message);
      setError("ไม่สามารถโหลดข้อมูลการซื้อได้");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (customerId) {
      loadPurchases();
    }
  }, [customerId]);

  if (loading) return <div>⏳ กำลังโหลดข้อมูลการซื้อ...</div>;
  if (error) return <div className="error-message">❌ {error}</div>;

  return (
    <div className="customer-purchases">
      <h3>🛒 การซื้อของฉัน</h3>
      {purchases.length > 0 ? (
        <ul className="purchase-list">
          {purchases.map((purchase) => (
            <li key={purchase.order_id} className="purchase-item">
              <p>
                <strong>ประเภทกรมธรรม์:</strong> {purchase.policy_type || "ไม่ระบุ"}
              </p>
              <p>
                <strong>บริษัทประกันภัย:</strong> {purchase.insurance_company || "ไม่ระบุ"}
              </p>
              <p>
                <strong>รถยนต์:</strong> {purchase.car_brand} {purchase.car_model}{" "}
                {purchase.car_submodel || "ไม่ระบุ"} ({purchase.car_year || "ไม่ระบุ"})
              </p>
              <p>
                <strong>ประเภทประกัน:</strong> {purchase.insurance_type || "ไม่ระบุ"}
              </p>
              <p>
                <strong>จำนวนเงิน:</strong> {purchase.total_price.toLocaleString()} บาท
              </p>
              <p>
                <strong>VAT:</strong> {purchase.vat.toLocaleString()} บาท
              </p>
              <p>
                <strong>อากรแสตมป์:</strong> {purchase.duty.toLocaleString()} บาท
              </p>
              <p>
                <strong>วันที่คุ้มครอง:</strong> {purchase.coverage_start_date || "ไม่ระบุ"} -{" "}
                {purchase.coverage_end_date || "ไม่ระบุ"}
              </p>
              <p>
                <strong>สถานะ:</strong>{" "}
                <span
                  className={`status-tag ${
                    purchase.payment_status === "success"
                      ? "success"
                      : purchase.payment_status === "pending"
                      ? "pending"
                      : "failed"
                  }`}
                >
                  {purchase.payment_status}
                </span>
              </p>
              <p>
                <strong>คูปองที่ใช้:</strong> {purchase.coupon_code || "ไม่ได้ใช้คูปอง"}
              </p>
              <p>
                <strong>Add-Ons:</strong>{" "}
                {purchase.add_ons
                  ? purchase.add_ons.split(",").map((addOn, index) => (
                      <span key={index} className="add-on-tag">
                        {addOn}
                      </span>
                    ))
                  : "ไม่มี"}
              </p>
              <button
                onClick={() => window.open(`/api/documents/uploads/${purchase.document_url}`, "_blank")}
                className="view-document-button"
              >
                👁️ ดูเอกสาร
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p>ไม่มีประวัติการซื้อ</p>
      )}
    </div>
  );
};

export default CustomerPurchases;
