
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

/**
 * Upload a PDF document to the ResearchMate backend.
 *
 * @param {File} file - The PDF selected by the user.
 * @returns {Promise<Object>} The backend upload response.
 */
export async function uploadDocument(file) {
  if (!file) {
    throw new Error('Please select a PDF document.');
  }

  const formData = new FormData();

  // The field name must be "file" to match FastAPI.
  formData.append('file', file);

  const response = await fetch(
    `${API_BASE_URL}/documents/upload`,
    {
      method: 'POST',
      body: formData,
    }
  );

  const result = await response.json();

  if (!response.ok) {
    throw new Error(
      result.detail || 'Document upload failed.'
    );
  }

  return result;
}

export async function checkBackendHealth() {
  const response = await fetch(
    `${API_BASE_URL}/health`
  );

  if (!response.ok) {
    throw new Error('Backend connection failed.');
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
    `${API_BASE_URL}/documents`
  );

  const result = await response.json();

  if (!response.ok) {
    throw new Error(
      result.detail || 'Failed to retrieve documents.'
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
    throw new Error('A document ID is required.');
  }

  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}`,
    {
      method: 'DELETE',
    }
  );

  const result = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      result.detail || 'Failed to delete document.'
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
    throw new Error('A document ID is required.');
  }

  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}`
  );

  const result = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      result.detail || 'Failed to retrieve document details.'
    );
  }

  return result;
}