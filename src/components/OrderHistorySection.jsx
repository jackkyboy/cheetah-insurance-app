/*/Users/apichet/Downloads/cheetah-insurance-app/src/components/OrderHistorySection.jsx */
import React from "react";
import "../assets/styles/OrderHistorySection.css";

const OrderHistorySection = ({ orderHistory = [] }) => {
  const renderOrderHistory = () => {
    if (orderHistory.length === 0) {
      return <p>ไม่มีคำสั่งซื้อที่เกี่ยวข้องกับผู้ใช้นี้</p>;
    }

    return (
      <ul className="order-history-list">
        {orderHistory.map((order) => {
          const orderDate = order.created_at
            ? new Date(order.created_at).toLocaleString()
            : "ไม่ระบุวันที่";
          const totalPrice = order.total_price
            ? `${order.total_price.toLocaleString()} บาท`
            : "ไม่ระบุราคา";

          return (
            <li key={order.order_id} className="order-history-item">
              <p>
                <strong>หมายเลขคำสั่งซื้อ:</strong> {order.order_id || "ไม่ระบุ"}
              </p>
              <p>
                <strong>สถานะ:</strong> {order.payment_status || "ไม่ระบุสถานะ"}
              </p>
              <p>
                <strong>ราคา:</strong> {totalPrice}
              </p>
              <p>
                <strong>วันที่:</strong> {orderDate}
              </p>
              <p>
                <a
                  href={`/order/${order.order_id}`}
                  className="view-order-link"
                  onClick={(e) => {
                    if (!order.order_id) {
                      e.preventDefault();
                      alert("ไม่สามารถดูคำสั่งซื้อนี้ได้");
                    }
                  }}
                >
                  ดูรายละเอียด
                </a>
              </p>
            </li>
          );
        })}
      </ul>
    );
  };

  return (
    <div className="order-history-section">
      <h3>ประวัติคำสั่งซื้อ</h3>
      {renderOrderHistory()}
    </div>
  );
};

export default OrderHistorySection;
