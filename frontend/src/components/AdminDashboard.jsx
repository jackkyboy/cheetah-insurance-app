// /Users/apichet/Downloads/cheetah-insurance-app/src/components/AdminDashboard.jsx
// /Users/apichet/Downloads/cheetah-insurance-app/src/components/AdminDashboard.jsx
import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { fetchDashboardStats } from "../api/adminDashboardService";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import { Pie, Bar } from "react-chartjs-2";
import "../assets/styles/AdminDashboard.css";
import "boxicons/css/boxicons.min.css";

ChartJS.register(ArcElement, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const AdminDashboard = () => {
  const { authToken, user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const calculateTotalRevenue = (orders = []) =>
    orders?.filter(o => o.payment_status === "completed")
      .reduce((sum, o) => sum + (o.total_price || 0), 0) || 0;

  const calculateInsuranceTypes = (orders = []) => {
    const typeCounts = {};
    orders?.forEach(o => {
      if (o.insurance_type) typeCounts[o.insurance_type] = (typeCounts[o.insurance_type] || 0) + 1;
    });
    return { labels: Object.keys(typeCounts), data: Object.values(typeCounts) };
  };

  const calculateMonthlySales = (orders = []) => {
    const sales = {};
    orders?.forEach(o => {
      if (o.created_at && o.total_price) {
        const month = new Date(o.created_at).toLocaleString("en-US", { month: "short", year: "numeric" });
        sales[month] = (sales[month] || 0) + o.total_price;
      }
    });
    return { labels: Object.keys(sales), data: Object.values(sales) };
  };

  useEffect(() => {
    if (!authToken) {
      setError("Authentication required.");
      setLoading(false);
      return;
    }

    fetchDashboardStats(authToken)
      .then(data => {
        const updated = {
          ...data,
          totalRevenue: calculateTotalRevenue(data.orders),
          insuranceDistribution: calculateInsuranceTypes(data.orders),
          monthlySales: calculateMonthlySales(data.orders),
        };
        setStats(updated);
        setLoading(false);
      })
      .catch(err => {
        console.error("Dashboard error", err);
        setError("Failed to load dashboard");
        setLoading(false);
      });
  }, [authToken]);

  if (loading) return <div className="dashboard-container">⌛ Loading...</div>;
  if (error) return <div className="dashboard-container error-message">{error}</div>;

  return (
    <div className="admin-dashboard">
      {/* Sidebar */}
      <section id="sidebar">
        <a href="#" className="brand"><i className='bx bxs-smile'></i><span className="text">AdminHub</span></a>
        <ul className="side-menu top">
          <li className="active"><a href="#"><i className='bx bxs-dashboard'></i><span>Dashboard</span></a></li>
          <li><a href="#"><i className='bx bxs-group'></i><span>Users</span></a></li>
        </ul>
        <ul className="side-menu bottom">
          <li><a href="#"><i className='bx bxs-cog'></i><span>Settings</span></a></li>
          <li><a href="#" onClick={logout}><i className='bx bx-power-off'></i><span>Logout</span></a></li>
        </ul>
      </section>

      {/* Content */}
      <section id="content">
        <nav>
          <i className='bx bx-menu'></i>
          <form><input type="text" placeholder="Search..." /></form>
          <div className="profile"><img src="https://placehold.co/40x40" alt="admin" /></div>
        </nav>

        <main>
          <div className="head-title">
            <h1>Welcome, {user?.email || "Admin"}</h1>
          </div>

          <ul className="box-info">
            <li><i className='bx bxs-group'></i><span><h3>{stats.total_customers}</h3><p>Total Users</p></span></li>
            <li><i className='bx bxs-receipt'></i><span><h3>{stats.total_payments}</h3><p>Total Orders</p></span></li>
            <li><i className='bx bxs-dollar-circle'></i><span><h3>฿{stats.totalRevenue.toLocaleString()}</h3><p>Revenue</p></span></li>
          </ul>

          <div className="charts">
            <div className="chart-card">
              <h3>Insurance Distribution</h3>
              {stats.insuranceDistribution.labels.length > 0 ? (
                <Pie data={{
                  labels: stats.insuranceDistribution.labels,
                  datasets: [{ data: stats.insuranceDistribution.data, backgroundColor: ["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0", "#9966FF"] }]
                }} />
              ) : <p>No data available</p>}
            </div>

            <div className="chart-card">
              <h3>Sales by Month</h3>
              {stats.monthlySales.labels.length > 0 ? (
                <Bar data={{
                  labels: stats.monthlySales.labels,
                  datasets: [{ label: "Sales", data: stats.monthlySales.data, backgroundColor: "#36A2EB" }]
                }} />
              ) : <p>No data available</p>}
            </div>
          </div>
        </main>
      </section>
    </div>
  );
};

export default AdminDashboard;
