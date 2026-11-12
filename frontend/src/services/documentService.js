
const API_BASE_URL = `${
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
}/api/v1`;

/**
 * Upload a PDF document to the ResearchMate backend.
 *
 * @param {File} file - The PDF selected by the user.
 * @returns {Promise<Object>} The backend upload response.
 */
export async function uploadDocument(file) {
  if (!file) {
    throw new Error("Please select a PDF document.");
  }

  const formData = new FormData();

  // The field name must be "file" to match FastAPI.
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/documents/upload`,
    {
      method: "POST",
      credentials: "include",
      body: formData,
    }
  );

  const result = await response.json();

  if (!response.ok) {
    throw new Error(
      result.detail || "Document upload failed."
    );
  }

  return result;
}


export async function checkBackendHealth() {
  const response = await fetch(
    `${API_BASE_URL}/health`,
    {
      credentials: "include",
    }
  );

  if (!response.ok) {
    throw new Error("Backend connection failed.");
  }

  return response.json();
}


/**
 * Retrieve all documents stored in ResearchMate AI.
 *
 * @returns {Promise<Object>} The document list from the backend.
 */
export async function getDocuments() {
  const response = await fetch(
    `${API_BASE_URL}/documents`,
    {
      credentials: "include",
    }
  );

  const result = await response.json();

  if (!response.ok) {
    throw new Error(
      result.detail || "Failed to retrieve documents."
    );
  }

  return result;
}


/**
 * Delete a document from ResearchMate AI.
 *
 * @param {string} documentId - Unique identifier of the document.
 * @returns {Promise<Object>} The backend deletion response.
 */
export async function deleteDocument(documentId) {
  if (!documentId) {
    throw new Error("A document ID is required.");
  }

  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}`,
    {
      method: "DELETE",
      credentials: "include",
    }
  );

  const result = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      result.detail || "Failed to delete document."
    );
  }

  return result;
}


/**
 * Retrieve details of a specific document.
 *
 * @param {string} documentId - Unique identifier of the document.
 * @returns {Promise<Object>} The document details from the backend.
 */
export async function getDocumentDetails(documentId) {
  if (!documentId) {
    throw new Error("A document ID is required.");
  }

  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}`,
    {
      credentials: "include",
    }
  );

  const result = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      result.detail || "Failed to retrieve document details."
    );
  }

  return result;
}


/**
 * Send a research question to the ResearchMate AI backend.
 *
 * @param {string} question - The user's research question.
 * @param {number} topK - Number of relevant passages to retrieve.
 * @param {number|null} conversationId - Existing conversation ID, if any.
 * @returns {Promise<Object>} The AI-generated answer and supporting evidence.
 */
export async function queryResearchAssistant(
  question,
  topK = 5,
  conversationId = null
) {
  if (!question || !question.trim()) {
    throw new Error("Please enter a research question.");
  }

  const response = await fetch(
    `${API_BASE_URL}/chat/query`,
    {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: question.trim(),
        top_k: topK,
        conversation_id: conversationId,
      }),
    }
  );

  const result = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      result.detail || "Failed to get a response from ResearchMate AI."
    );
  }

  return result;
}


/**
 * Generate a URL for opening an original PDF at a cited page.
 */
export function getDocumentFileUrl(documentId, pageNumber) {
  if (!documentId) {
    throw new Error("A document ID is required.");
  }

  const url = `${API_BASE_URL}/documents/${encodeURIComponent(documentId)}/file`;

  return `${url}#page=${Math.max(1, Number(pageNumber) || 1)}`;
}


/**
 * Retrieve all saved research conversations.
 */
export async function getConversations() {
  const response = await fetch(
    `${API_BASE_URL}/conversations`,
    {
      credentials: "include",
    }
  );

  const result = await response.json().catch(() => []);

  if (!response.ok) {
    throw new Error(
      result.detail || "Failed to retrieve research history."
    );
  }

  return result;
}


/**
 * Retrieve a specific conversation and its messages.
 *
 * @param {number} conversationId
 */
export async function getConversation(conversationId) {
  if (!conversationId) {
    throw new Error("A conversation ID is required.");
  }

  const response = await fetch(
    `${API_BASE_URL}/conversations/${conversationId}`,
    {
      credentials: "include",
    }
  );

  const result = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      result.detail || "Failed to retrieve conversation."
    );
  }

  return result;
}


/**
 * Rename an existing research conversation.
 *
 * @param {number} conversationId
 * @param {string} title
 */
export async function renameConversation(conversationId, title) {
  if (!conversationId) {
    throw new Error("A conversation ID is required.");
  }

  if (!title || !title.trim()) {
    throw new Error("A conversation title is required.");
  }

  const response = await fetch(
    `${API_BASE_URL}/conversations/${conversationId}`,
    {
      method: "PATCH",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: title.trim(),
      }),
    }
  );

  const result = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      result.detail || "Failed to rename conversation."
    );
  }

  return result;
}


/**
 * Delete a research conversation.
 *
 * @param {number} conversationId
 */
export async function deleteConversation(conversationId) {
  if (!conversationId) {
    throw new Error("A conversation ID is required.");
  }

  const response = await fetch(
    `${API_BASE_URL}/conversations/${conversationId}`,
    {
      method: "DELETE",
      credentials: "include",
    }
  );

  if (!response.ok) {
    const result = await response.json().catch(() => ({}));

    throw new Error(
      result.detail || "Failed to delete conversation."
    );
  }

  return true;
}
