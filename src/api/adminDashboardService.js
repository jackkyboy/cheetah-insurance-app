// /Users/apichet/Downloads/cheetah-insurance-app/src/api/adminDashboardService.js
import axiosInstance from "./axiosInstance";
import { getAuthToken, refreshAccessToken, adminLogout } from "./adminAuthService";

/**
 * ✅ Utility function to attach headers with Authorization token
 */
const getAuthHeaders = async () => {
    let authToken = getAuthToken();
    let refreshToken = localStorage.getItem("refreshToken");

    console.log(`[${new Date().toISOString()}] 🔍 Checking Tokens`, { authToken, refreshToken });

    if (!authToken) {
        if (refreshToken) {
            console.warn(`[${new Date().toISOString()}] 🔄 No Auth Token found! Trying to refresh...`);
            try {
                authToken = await refreshAccessToken();
                if (!authToken) throw new Error("❌ Refresh token failed");

                console.log(`[${new Date().toISOString()}] ✅ New Access Token received:`, authToken);
            } catch (err) {
                console.error(`[${new Date().toISOString()}] ❌ Token Refresh Failed:`, err.message);
                adminLogout();
                return null;  // ✅ ป้องกัน React พัง
            }
        } else {
            console.error(`[${new Date().toISOString()}] ❌ No Admin Token Found. Logging Out.`);
            adminLogout();
            return null;  // ✅ ป้องกัน React พัง
        }
    }

    console.log(`[${new Date().toISOString()}] 🔑 Final Auth Token being used:`, authToken);
    return { Authorization: `Bearer ${authToken}` };
};

/**
 * 📊 ดึงข้อมูล Dashboard สำหรับ Admin
 */
export const fetchDashboardStats = async () => {
    try {
        console.log(`[${new Date().toISOString()}] 🔍 Fetching Admin Dashboard Data...`);

        const headers = await getAuthHeaders();
        if (!headers) return null;

        const response = await axiosInstance.get("/admins/dashboard-stats", { headers });

        console.log(`[${new Date().toISOString()}] ✅ API Response:`, response.data);

        if (!response.data || typeof response.data !== "object") {
            throw new Error("❌ Invalid API response format");
        }

        if (typeof response.data.totalRevenue !== "number") {
            console.warn(`[${new Date().toISOString()}] ⚠️ Warning: totalRevenue is not a number!`, response.data.totalRevenue);
        }

        return {
            ...response.data,
            totalRevenue: response.data.totalRevenue ?? 0,  // ✅ ป้องกัน `undefined`
            insuranceDistribution: response.data.insuranceDistribution ?? { labels: [], data: [] },
            monthlySales: response.data.monthlySales ?? { labels: [], data: [] },
        };
    } catch (error) {
        console.error(`[${new Date().toISOString()}] ❌ Error fetching dashboard stats:`, error.response?.data || error.message);

        if (error.response?.status === 401) {
            console.warn(`[${new Date().toISOString()}] ⚠️ Unauthorized! Redirecting to login...`);
            adminLogout();
        }

        return null;
    }
};

/**
 * 🔄 ดึง Users ที่ Pending อนุมัติ
 */
export const fetchPendingUsers = async (page = 1, per_page = 10) => {
    try {
        console.log(`[${new Date().toISOString()}] 🔍 Fetching pending users: page=${page}, per_page=${per_page}`);

        const headers = await getAuthHeaders();
        if (!headers) return [];

        const response = await axiosInstance.get(`/admins/pending-users?page=${page}&per_page=${per_page}`, { headers });

        console.log(`[${new Date().toISOString()}] ✅ Pending Users Response:`, response.data);
        return response.data || [];  // ✅ ป้องกัน `null`
    } catch (error) {
        console.error(`[${new Date().toISOString()}] ❌ Error fetching pending users:`, error.response?.data || error.message);

        if (error.response?.status === 401) {
            console.warn(`[${new Date().toISOString()}] ⚠️ Unauthorized! Redirecting to login...`);
            adminLogout();
        }

        return [];
    }
};

/**
 * ✅ อนุมัติ User
 */
export const approveUser = async (userId, stats, setStats) => {
    try {
        console.log(`[${new Date().toISOString()}] 🔍 Approving user ID: ${userId}`);

        const headers = await getAuthHeaders();
        if (!headers) return;

        const response = await axiosInstance.post("/admins/approve-user", { user_id: userId }, { headers });

        console.log(`[${new Date().toISOString()}] ✅ Approve User Response:`, response.data);

        // ✅ อัปเดต Pending Users ทันทีหลังจาก Approve
        setStats((prevStats) => ({
            ...prevStats,
            pending_users: prevStats.pending_users.filter((user) => user.user_id !== userId),
        }));

        return response.data;
    } catch (error) {
        console.error(`[${new Date().toISOString()}] ❌ Error approving user (ID: ${userId}):`, error.response?.data || error.message);

        if (error.response?.status === 401) {
            console.warn(`[${new Date().toISOString()}] ⚠️ Unauthorized! Redirecting to login...`);
            adminLogout();
        }
    }
};

/**
 * ❌ ปฏิเสธ User
 */
export const rejectUser = async (userId, stats, setStats) => {
    try {
        console.log(`[${new Date().toISOString()}] 🔍 Rejecting user ID: ${userId}`);

        const headers = await getAuthHeaders();
        if (!headers) return;

        const response = await axiosInstance.post("/admins/reject-user", { user_id: userId }, { headers });

        console.log(`[${new Date().toISOString()}] ✅ Reject User Response:`, response.data);

        // ✅ อัปเดต Pending Users ทันทีหลังจาก Reject
        setStats((prevStats) => ({
            ...prevStats,
            pending_users: prevStats.pending_users.filter((user) => user.user_id !== userId),
        }));

        return response.data;
    } catch (error) {
        console.error(`[${new Date().toISOString()}] ❌ Error rejecting user (ID: ${userId}):`, error.response?.data || error.message);

        if (error.response?.status === 401) {
            console.warn(`[${new Date().toISOString()}] ⚠️ Unauthorized! Redirecting to login...`);
            adminLogout();
        }
    }
};
