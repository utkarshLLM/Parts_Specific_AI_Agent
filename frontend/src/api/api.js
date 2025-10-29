/**
 * API Service
 * Handles communication with the backend at http://localhost:5000/api/chat
 */

// Backend URL - Make sure this matches where your backend is running
const BACKEND_URL = "http://localhost:5001/api/chat";;

// Store session ID to maintain conversation continuity
let currentSessionId = null;

/**
 * Get AI Message from Backend
 * Sends user query to backend and returns formatted response
 * @param {string} userQuery - The user's message
 * @returns {Promise<Object>} - Formatted message object with role and content
 */
export const getAIMessage = async (userQuery) => {
  try {
    // 1. Prepare request payload
    const payload = {
      message: userQuery,
      sessionId: currentSessionId, // Include session ID if we have one (for conversation continuity)
    };

    console.log("📤 Sending to backend:", payload); // Debug log

    // 2. Send POST request to backend
    const response = await fetch(BACKEND_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    console.log("📥 Response status:", response.status); // Debug log

    // 3. Check if response is OK
    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    // 4. Parse response JSON
    const data = await response.json();

    console.log("📥 Response data:", data); // Debug log

    // 5. Save session ID for next request (maintains conversation)
    if (data.sessionId) {
      currentSessionId = data.sessionId;
      console.log("💾 Session ID saved:", currentSessionId); // Debug log
    }

    // 6. Format response based on response type
    const formattedMessage = formatBackendResponse(data);

    return formattedMessage;
  } catch (error) {
    // Handle errors
    console.error("❌ Error calling backend:", error);

    return {
      role: "assistant",
      content: `Sorry, I encountered an error: ${error.message}. Please make sure the backend is running on http://localhost:5000`,
    };
  }
};

/**
 * Format Backend Response
 * Takes the backend response and formats it based on response type
 * @param {Object} data - Response data from backend
 * @returns {Object} - Formatted message object
 */
const formatBackendResponse = (data) => {
  // Check if request was successful
  if (!data.success) {
    return {
      role: "assistant",
      content: data.error?.message || "An error occurred",
    };
  }

  const response = data.response;
  let content = "";

  // Format content based on response type
  switch (response.type) {
    // Text response - just return the content
    case "text":
      content = response.content;
      break;

    // Product results - format as list
    case "product_results":
      content = formatProductResults(response);
      break;

    // Installation guide - format with steps
    case "installation_guide":
      content = formatInstallationGuide(response);
      break;

    // Troubleshooting - format with causes and solutions
    case "troubleshooting":
      content = formatTroubleshooting(response);
      break;

    // Out of scope - friendly deflection
    case "out_of_scope":
      content = response.content;
      break;

    // Error response
    case "error":
      content = `Error: ${response.content}`;
      break;

    // Unknown type - just show content
    default:
      content = response.content;
  }

  return {
    role: "assistant",
    content: content,
  };
};

/**
 * Format Product Results
 * Formats product data into readable list
 * @param {Object} response - Response with product data
 * @returns {string} - Formatted product list
 */
const formatProductResults = (response) => {
  const { content, data } = response;

  if (!data || !data.products || data.products.length === 0) {
    return content || "No products found";
  }

  let formatted = content + "\n\n";

  data.products.forEach((product, index) => {
    formatted += `**${index + 1}. ${product.name}**\n`;
    formatted += `   ID: ${product.id}\n`;
    formatted += `   Price: $${product.price}\n`;
    formatted += `   Description: ${product.description}\n`;
    if (product.compatibility && product.compatibility.length > 0) {
      formatted += `   Compatible with: ${product.compatibility.join(", ")}\n`;
    }
    formatted += `   In Stock: ${product.inStock ? "Yes" : "No"}\n\n`;
  });

  return formatted;
};

/**
 * Format Installation Guide
 * Formats installation steps into readable format
 * @param {Object} response - Response with installation data
 * @returns {string} - Formatted installation guide
 */
const formatInstallationGuide = (response) => {
  const { content, data } = response;

  if (!data || !data.steps || data.steps.length === 0) {
    return content || "No installation steps available";
  }

  let formatted = content + "\n\n";
  formatted += `⏱️ Estimated Time: ${data.estimatedTime} minutes\n`;
  formatted += `📊 Difficulty: ${data.difficulty}\n\n`;

  data.steps.forEach((step) => {
    formatted += `**Step ${step.step}: ${step.instruction}**\n`;

    if (step.tools && step.tools.length > 0) {
      formatted += `   🔧 Tools needed: ${step.tools.join(", ")}\n`;
    }

    if (step.tips && step.tips.length > 0) {
      formatted += `   💡 Tips:\n`;
      step.tips.forEach((tip) => {
        formatted += `      - ${tip}\n`;
      });
    }

    if (step.warnings && step.warnings.length > 0) {
      formatted += `   ⚠️ Warnings:\n`;
      step.warnings.forEach((warning) => {
        formatted += `      - ${warning}\n`;
      });
    }

    formatted += "\n";
  });

  return formatted;
};

/**
 * Format Troubleshooting
 * Formats troubleshooting causes and solutions
 * @param {Object} response - Response with troubleshooting data
 * @returns {string} - Formatted troubleshooting guide
 */
const formatTroubleshooting = (response) => {
  const { content, data } = response;

  let formatted = content + "\n\n";

  // Format possible causes
  if (data && data.possibleCauses && data.possibleCauses.length > 0) {
    formatted += "**Possible Causes:**\n\n";

    data.possibleCauses.forEach((cause, index) => {
      formatted += `${index + 1}. **${cause.cause}** (${cause.probability} probability)\n`;
      formatted += `   Description: ${cause.description}\n`;
      formatted += `   Fix: ${cause.fix}\n\n`;
    });
  }

  // Format suggested solutions
  if (data && data.suggestedSolutions && data.suggestedSolutions.length > 0) {
    formatted += "**Suggested Solutions:**\n\n";

    data.suggestedSolutions.forEach((solution, index) => {
      formatted += `**Solution ${index + 1}: ${solution.title}**\n`;

      if (solution.steps && solution.steps.length > 0) {
        solution.steps.forEach((step, stepIndex) => {
          formatted += `   ${stepIndex + 1}. ${step}\n`;
        });
      }

      formatted += `   ⏱️ Estimated Time: ${solution.estimatedTime} minutes\n`;

      if (solution.recommendedParts && solution.recommendedParts.length > 0) {
        formatted += `   🛠️ Recommended Parts: ${solution.recommendedParts.join(", ")}\n`;
      }

      formatted += "\n";
    });
  }

  return formatted;
};

/**
 * Reset Session
 * Call this if you want to start a new conversation
 */
export const resetSession = () => {
  currentSessionId = null;
  console.log("🔄 Session reset");
};

/**
 * Get Current Session ID
 * For debugging purposes
 */
export const getCurrentSessionId = () => {
  return currentSessionId;
};