/*/Users/apichet/Downloads/cheetah-insurance-app/src/api/paymentService.js */
import axios from "./axios"; // Adjust the path if your axios instance is configured elsewhere

/**
 * Validate payload structure
 * @param {Object} payload - The payload containing payment details
 * @param {Array} requiredFields - List of required fields
 * @throws {Error} If validation fails
 */
const validatePayload = (payload, requiredFields) => {
  const missingFields = requiredFields.filter(
    (field) => !payload[field] || payload[field] === ""
  );
  if (missingFields.length > 0) {
    throw new Error(`Missing required fields: ${missingFields.join(", ")}`);
  }
};

/**
 * Create a new payment order and redirect to the payment page.
 * @param {Object} payload - The payload containing payment details
 * @returns {Promise<Object>} - Payment order response
 */
export const createPaymentOrder = async (payload) => {
  try {
    // ✅ Validate payload before sending the request
    validatePayload(payload, ["customer_id", "amount", "currency"]);

    const response = await axios.post("/payments/create", payload);
    console.log("✅ [PaymentService] Payment Order Created:", response.data);

    // ✅ Extract JWT payload from backend response
    const jwtPayload = response.data?.payload;
    if (!jwtPayload) {
      console.error("❌ Missing JWT payload in response.");
      throw new Error("Missing JWT payload in response.");
    }

    // ✅ Decode the middle part of the JWT to extract webPaymentUrl
    const decoded = JSON.parse(atob(jwtPayload.split(".")[1]));
    const webPaymentUrl = decoded.webPaymentUrl;

    // ✅ Ensure the `webPaymentUrl` exists
    if (!webPaymentUrl) {
      console.error("❌ webPaymentUrl is missing in the decoded JWT.");
      throw new Error("webPaymentUrl is missing in the decoded JWT.");
    }

    console.log("🔗 Redirecting user to:", webPaymentUrl);

    // ✅ Redirect the user to the external payment page
    window.location.href = webPaymentUrl;

    return response.data; // Return for debugging/logging purposes
  } catch (error) {
    console.error(
      "❌ [PaymentService] Error creating payment order:",
      error.response?.data || error.message
    );
    throw error.response?.data || new Error("Failed to create payment order");
  }
};


/**
 * Fetch available payment options for a given payment token
 * @param {String} paymentToken - The payment token from 2C2P
 * @returns {Promise<Object>} - Available payment options
 */
export const fetchPaymentOptions = async (paymentToken) => {
  try {
    // Validate paymentToken
    if (!paymentToken) {
      throw new Error("Payment token is required.");
    }

    const response = await axios.post("/payments/options", {
      payment_token: paymentToken, // Include the payment token in the request body
    });
    console.log("✅ [PaymentService] Payment Options Fetched:", response.data);
    return response.data; // Return the payment options response
  } catch (error) {
    console.error(
      "❌ [PaymentService] Error fetching payment options:",
      error.response?.data || error.message
    );
    // Throw the error response or a default error
    throw error.response?.data || new Error("Failed to fetch payment options");
  }
};

/**
 * Get payment status by order ID
 * @param {String} orderId - The order ID of the payment
 * @returns {Promise<Object>} - Payment status response
 */
export const getPaymentStatus = async (orderId) => {
  try {
    // Validate orderId
    if (!orderId) {
      throw new Error("Order ID is required.");
    }

    const response = await axios.get(`/payments/status/${orderId}`);
    console.log("✅ [PaymentService] Payment Status Fetched:", response.data);
    return response.data; // Return the payment status from the backend
  } catch (error) {
    console.error(
      "❌ [PaymentService] Error fetching payment status:",
      error.response?.data || error.message
    );
    // Throw the error response or a default error
    throw error.response?.data || new Error("Failed to fetch payment status");
  }
};

/**
 * Generate a payment URL for redirection
 * @param {Object} payload - The payload with payment details
 * @returns {Promise<String>} - The payment redirection URL
 */
export const generatePaymentUrl = async (payload) => {
  try {
    // Validate payload
    validatePayload(payload, ["amount", "order_id"]);

    const response = await axios.post("/payments/generate-url", payload);
    console.log("✅ [PaymentService] Payment URL Generated:", response.data);

    // Ensure the paymentUrl exists
    const paymentUrl = response.data.paymentUrl;
    if (!paymentUrl) {
      console.error("❌ Payment URL is missing in the response.");
      throw new Error("Payment URL is missing in the response.");
    }

    return paymentUrl; // Return the generated payment URL
  } catch (error) {
    console.error(
      "❌ [PaymentService] Error generating payment URL:",
      error.response?.data || error.message
    );
    // Throw the error response or a default error
    throw error.response?.data || new Error("Failed to generate payment URL");
  }
};
