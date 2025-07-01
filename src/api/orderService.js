// /Users/apichet/Downloads/cheetah-insurance-app/src/api/orderService.js
import axios from "axios";

// Define the base API URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:5000/api";

/**
 * Fetch order history for a specific customer.
 * 
 * @param {number} customerId - The ID of the customer whose orders are to be fetched.
 * @returns {Array} - An array of order objects or an empty array if no orders are found.
 * @throws {Error} - Throws an error if fetching orders fails for any reason.
 */
export const fetchOrderHistory = async (customerId) => {
  try {
    if (!customerId) {
      throw new Error("Customer ID is required to fetch order history.");
    }

    console.info(`📡 Fetching order history for customer_id=${customerId}`);

    // Make the API call to fetch orders
    const response = await axios.get(`${API_BASE_URL}/payments/orders/customer/${customerId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("authToken")}`, // Include the auth token in the header
      },
    });

    // Check for orders in the response
    if (response.data?.orders && response.data.orders.length > 0) {
      console.info(`✅ Found ${response.data.orders.length} orders for customer_id=${customerId}`);
    } else {
      console.info(`⚠️ No orders found for customer_id=${customerId}`);
    }

    // Return the orders array or an empty array if undefined
    return response.data.orders || [];
  } catch (error) {
    // Handle 404 error (no orders found)
    if (error.response?.status === 404) {
      console.warn(`⚠️ No orders found for customer_id=${customerId}`);
      return []; // Return an empty array for graceful handling
    }

    // Handle unauthorized error (401)
    if (error.response?.status === 401) {
      console.error("❌ Unauthorized access. Please check the authentication token.");
      throw new Error("Unauthorized access. Please log in again.");
    }

    // Log and rethrow other errors
    console.error("❌ Error fetching order history:", error.response?.data?.error || error.message);
    throw new Error("Failed to fetch order history.");
  }
};

/**
 * Fetch the status of a specific order.
 * 
 * @param {string} orderId - The unique ID of the order to fetch.
 * @returns {Object} - The order details.
 * @throws {Error} - Throws an error if the order is not found or the request fails.
 */
export const fetchOrderStatus = async (orderId) => {
  try {
    if (!orderId) {
      throw new Error("Order ID is required to fetch order status.");
    }

    console.info(`📡 Fetching order status for order_id=${orderId}`);

    // Make the API call to fetch the order status
    const response = await axios.get(`${API_BASE_URL}/payments/orders/${orderId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("authToken")}`, // Include the auth token in the header
      },
    });

    console.info(`✅ Successfully fetched order status for order_id=${orderId}`);
    return response.data || {};
  } catch (error) {
    // Handle 404 error (order not found)
    if (error.response?.status === 404) {
      console.warn(`⚠️ Order not found for order_id=${orderId}`);
      throw new Error("Order not found.");
    }

    // Log and rethrow other errors
    console.error("❌ Error fetching order status:", error.response?.data?.error || error.message);
    throw new Error("Failed to fetch order status.");
  }
};
