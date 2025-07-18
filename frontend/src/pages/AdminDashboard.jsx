// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/AdminDashboard.jsx
// /Users/apichet/Downloads/cheetah-insurance-app/src/pages/AdminDashboard.jsx
import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { fetchDashboardStats, approveUser, rejectUser } from "../api/adminDashboardService";
import { Chart as ChartJS, ArcElement, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from "chart.js";
import { Pie, Bar } from "react-chartjs-2";
import { Link } from "react-router-dom";
import "../assets/styles/AdminDashboard.css";

ChartJS.register(ArcElement, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const AdminDashboard = () => {
  const { authToken, user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => logout();

  const handleApproveUser = async (userId) => {
    try {
      await approveUser(authToken, userId);
      const updatedStats = await fetchDashboardStats(authToken);
      setStats(updatedStats);
    } catch (err) {
      alert("Error approving user: " + err.message);
    }
  };

  const handleRejectUser = async (userId) => {
    try {
      await rejectUser(authToken, userId);
      const updatedStats = await fetchDashboardStats(authToken);
      setStats(updatedStats);
    } catch (err) {
      alert("Error rejecting user: " + err.message);
    }
  };

  useEffect(() => {
    if (!authToken) {
      setError("Authentication required. Please log in again.");
      setLoading(false);
      return;
    }
    fetchDashboardStats(authToken)
      .then(setStats)
      .catch(() => setError("Failed to load dashboard data."))
      .finally(() => setLoading(false));
  }, [authToken]);

  if (loading) return <div className="dashboard-container">Loading...</div>;
  if (error) return <div className="dashboard-container error-message">{error}</div>;

  return (
    <div className={`admin-layout ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>
      {/* Sidebar */}
      <section id="sidebar">
        <Link to="#" className="brand"><i className="bx bxs-smile"></i><span className="text">AdminHub</span></Link>
        <ul className="side-menu top">
          <li className="active">
            <Link to="#"><i className="bx bxs-dashboard"></i><span className="text">Dashboard</span></Link>
          </li>
        </ul>
        <ul className="side-menu bottom">
          <li>
            <a href="#" className="logout" onClick={handleLogout}>
              <i className="bx bx-log-out-circle"></i><span className="text">Logout</span>
            </a>
          </li>
        </ul>
      </section>

      {/* Main content */}
      <section id="content">
        <nav>
          <i className="bx bx-menu" onClick={() => setSidebarOpen(!sidebarOpen)}></i>
          <span className="nav-link">Dashboard</span>
          <span className="admin-email">{user?.email}</span>
        </nav>

        <main>
          <div className="head-title">
            <div className="left">
              <h1>Dashboard</h1>
              <ul className="breadcrumb">
                <li><span>Dashboard</span></li>
              </ul>
            </div>
          </div>

          <ul className="box-info">
            <li>
              <i className="bx bxs-user"></i>
              <span className="text">
                <h3>{stats?.total_customers ?? 0}</h3>
                <p>Total Users</p>
              </span>
            </li>
            <li>
              <i className="bx bxs-cart-alt"></i>
              <span className="text">
                <h3>{stats?.total_payments ?? 0}</h3>
                <p>Total Sales</p>
              </span>
            </li>
            <li>
              <i className="bx bxs-dollar-circle"></i>
              <span className="text">
                <h3>฿{stats?.totalRevenue?.toLocaleString() ?? 0}</h3>
                <p>Total Revenue</p>
              </span>
            </li>
          </ul>

          <div className="charts-section">
            <div className="chart-container">
              <h3>Insurance Types</h3>
              {stats?.insuranceDistribution?.labels?.length ? (
                <Pie
                  data={{
                    labels: stats.insuranceDistribution.labels,
                    datasets: [{
                      data: stats.insuranceDistribution.data,
                      backgroundColor: ["#36A2EB", "#FF6384", "#FFCE56"]
                    }]
                  }}
                />
              ) : <p>No data</p>}
            </div>

            <div className="chart-container">
              <h3>Monthly Sales</h3>
              {stats?.monthlySales?.labels?.length ? (
                <Bar
                  data={{
                    labels: stats.monthlySales.labels,
                    datasets: [{
                      label: "Sales",
                      data: stats.monthlySales.data,
                      backgroundColor: "#36A2EB"
                    }]
                  }}
                  options={{ responsive: true, scales: { y: { beginAtZero: true } } }}
                />
              ) : <p>No data</p>}
            </div>
          </div>

          <div className="pending-users">
            <h2>Pending Approvals</h2>
            {stats?.pending_users?.length ? (
              <ul>
                {stats.pending_users.map((u) => (
                  <li key={u.user_id}>
                    <div className="user-info">
                      <strong>{u.email}</strong> — {u.name || "Unknown"}
                    </div>
                    <div className="action-buttons">
                      <button onClick={() => handleApproveUser(u.user_id)} className="approve-btn">✔ Approve</button>
                      <button onClick={() => handleRejectUser(u.user_id)} className="reject-btn">✖ Reject</button>
                    </div>
                  </li>
                ))}
              </ul>
            ) : <p>No pending users</p>}
          </div>
        </main>
      </section>
    </div>
  );
};

export default AdminDashboard;
