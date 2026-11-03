
import { useState, useEffect } from 'react';
import './App.css';

import {
  uploadDocument,
  getDocuments,
  deleteDocument,
  getDocumentDetails,
} from './services/documentService';

function App() {
  // PDF upload states
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [uploadError, setUploadError] = useState('');
  const [uploadedDocument, setUploadedDocument] = useState(null);

  // Document management states
  const [documents, setDocuments] = useState([]);
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const [documentsError, setDocumentsError] = useState('');
  const [deletingDocumentId, setDeletingDocumentId] = useState(null);

  // Document details states
  const [selectedDocumentDetails, setSelectedDocumentDetails] = useState(null);
  const [loadingDocumentDetails, setLoadingDocumentDetails] = useState(false);
  const [documentDetailsError, setDocumentDetailsError] = useState('');

  // Navigation state
  const [activeView, setActiveView] = useState('chat');

  // Fetch documents when the application loads
  useEffect(() => {
    async function loadDocuments() {
      try {
        setLoadingDocuments(true);
        setDocumentsError('');

        const result = await getDocuments();

        setDocuments(result.documents);
      } catch (error) {
        setDocumentsError(error.message);
      } finally {
        setLoadingDocuments(false);
      }
    }

    loadDocuments();
  }, []);

  // Handle PDF selection
  function handleFileChange(event) {
    const file = event.target.files[0];

    setUploadMessage('');
    setUploadError('');
    setUploadedDocument(null);

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setSelectedFile(null);
      setUploadError('Please select a PDF file.');
      event.target.value = '';
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      setSelectedFile(null);
      setUploadError('The file must not exceed 20 MB.');
      event.target.value = '';
      return;
    }

    setSelectedFile(file);
  }

  // Upload selected PDF
  async function handleUpload() {
    if (!selectedFile) {
      setUploadError('Please select a PDF document first.');
      return;
    }

    try {
      setUploading(true);
      setUploadError('');
      setUploadMessage('');

      const result = await uploadDocument(selectedFile);

      setUploadedDocument(result.document);
      setUploadMessage(result.message);
      setSelectedFile(null);

      // Refresh the document list after a successful upload
      const updatedDocuments = await getDocuments();
      setDocuments(updatedDocuments.documents);

    } catch (error) {
      setUploadError(error.message);
    } finally {
      setUploading(false);
    }
  }

  // Delete a document
  async function handleDeleteDocument(documentId) {
    const confirmDelete = window.confirm(
      'Are you sure you want to delete this document?'
    );

    if (!confirmDelete) {
      return;
    }

    try {
      setDeletingDocumentId(documentId);
      setDocumentsError('');

      await deleteDocument(documentId);

      // Remove the deleted document from the displayed list
      setDocuments((currentDocuments) =>
        currentDocuments.filter(
          (document) => document.document_id !== documentId
        )
      );

      // Close details if the deleted document was selected
      if (selectedDocumentDetails?.document_id === documentId) {
        setSelectedDocumentDetails(null);
      }

    } catch (error) {
      setDocumentsError(error.message);
    } finally {
      setDeletingDocumentId(null);
    }
  }

  // Retrieve details of a selected document
  async function handleViewDocumentDetails(documentId) {
    try {
      setLoadingDocumentDetails(true);
      setDocumentDetailsError('');
      setSelectedDocumentDetails(null);

      const result = await getDocumentDetails(documentId);

      setSelectedDocumentDetails(result);

    } catch (error) {
      setDocumentDetailsError(error.message);
    } finally {
      setLoadingDocumentDetails(false);
    }
  }

  return (
    <div className="app-container">

      {/* Sidebar */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">R</div>
          <h2>ResearchMate</h2>
        </div>

        <button className="new-chat-button">
          + New Research
        </button>

        {/* Sidebar Navigation */}
        <nav className="sidebar-nav">

          <p className="nav-heading">WORKSPACE</p>

          <a
            href="#"
            className={`nav-link ${activeView === 'chat' ? 'active' : ''}`}
            onClick={(event) => {
              event.preventDefault();
              setActiveView('chat');
            }}
          >
            <span>💬</span>
            Research Chat
          </a>

          <a
            href="#"
            className={`nav-link ${activeView === 'documents' ? 'active' : ''}`}
            onClick={(event) => {
              event.preventDefault();
              setActiveView('documents');
            }}
          >
            <span>📚</span>
            My Documents
          </a>

          <a
            href="#"
            className={`nav-link ${activeView === 'history' ? 'active' : ''}`}
            onClick={(event) => {
              event.preventDefault();
              setActiveView('history');
            }}
          >
            <span>📖</span>
            Research History
          </a>

        </nav>

        {/* Sidebar Bottom */}
        <div className="sidebar-bottom">

          <div className="user-profile">
            <div className="user-avatar">U</div>

            <div>
              <h4>Researcher</h4>
              <p>Personal Workspace</p>
            </div>
          </div>

        </div>

      </aside>

      {/* Main Workspace */}
      <main className="main-content">

        {/* Topbar */}
        <header className="topbar">

          <div>
            <h3>
              {activeView === 'chat'
                ? 'Research Chat'
                : activeView === 'documents'
                  ? 'My Documents'
                  : 'Research History'}
            </h3>

            <p>
              {activeView === 'chat'
                ? 'Ask questions and explore your research documents.'
                : activeView === 'documents'
                  ? 'Manage your uploaded research papers.'
                  : 'Review your previous research conversations.'}
            </p>
          </div>

          <div className="status-indicator">
            <span></span>
            AI Assistant
          </div>

        </header>

        {/* Research Chat Workspace */}
        {activeView === 'chat' && (

          <section className="chat-workspace">

            <div className="welcome-section">

              <div className="welcome-icon">✦</div>

              <h1>Your Research, Made Easier.</h1>

              <p>
                Upload your academic papers, ask research questions,
                and get evidence-based answers with page citations.
              </p>

            </div>

            {/* PDF Upload Section */}
            <div className="upload-section">

              <h3>Upload a Research Paper</h3>

              <p>
                Select an academic PDF to add it to your research workspace.
                Maximum file size: 20 MB.
              </p>

              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
              />

              {selectedFile && (
                <p>
                  Selected file: {selectedFile.name}
                </p>
              )}

              <button
                onClick={handleUpload}
                disabled={!selectedFile || uploading}
              >
                {uploading ? 'Uploading...' : 'Upload PDF'}
              </button>

              {uploadMessage && (
                <p>{uploadMessage}</p>
              )}

              {uploadError && (
                <p>{uploadError}</p>
              )}

              {uploadedDocument && (
                <div>

                  <h4>Document processed successfully</h4>

                  <p>
                    Filename: {uploadedDocument.filename}
                  </p>

                  <p>
                    Pages: {uploadedDocument.total_pages}
                  </p>

                  <p>
                    Chunks: {uploadedDocument.total_chunks}
                  </p>

                  <p>
                    Embeddings: {uploadedDocument.total_embeddings}
                  </p>

                </div>
              )}

            </div>

            {/* Research Suggestions */}
            <div className="suggestion-grid">

              <div className="suggestion-card">
                <span>🔍</span>
                <h4>Understand a paper</h4>
                <p>
                  Ask questions about your uploaded research papers.
                </p>
              </div>

              <div className="suggestion-card">
                <span>📑</span>
                <h4>Find evidence</h4>
                <p>
                  Retrieve relevant passages from your documents.
                </p>
              </div>

              <div className="suggestion-card">
                <span>📌</span>
                <h4>Track citations</h4>
                <p>
                  See which documents and pages support an answer.
                </p>
              </div>

            </div>

            {/* Chat Input */}
            <div className="chat-input-container">

              <textarea
                placeholder="Ask a question about your research..."
                rows="3"
              />

              <div className="chat-input-footer">

                <span>
                  ResearchMate AI uses your uploaded documents.
                </span>

                <button disabled>
                  Send ↗
                </button>

              </div>

            </div>

          </section>

        )}

        {/* My Documents Workspace */}
        {activeView === 'documents' && (

          <section className="chat-workspace">

            <div className="welcome-section">
              <h1>My Research Documents</h1>

              <p>
                View and manage the academic papers in your workspace.
              </p>
            </div>

            {loadingDocuments && (
              <p>Loading your documents...</p>
            )}

            {documentsError && (
              <p>{documentsError}</p>
            )}

            {!loadingDocuments &&
              !documentsError &&
              documents.length === 0 && (
                <p>You haven't uploaded any documents yet.</p>
              )}

            {!loadingDocuments &&
              !documentsError &&
              documents.length > 0 && (

                <div className="suggestion-grid">

                  {documents.map((document) => (

                    <div
                      className="suggestion-card"
                      key={document.document_id}
                    >

                      <span>📄</span>

                      <h4>{document.filename}</h4>

                      <p>
                        {document.total_chunks} text chunks
                      </p>

                      <button
                        onClick={() =>
                          handleViewDocumentDetails(document.document_id)
                        }
                        disabled={loadingDocumentDetails}
                      >
                        View Details
                      </button>

                      <button
                        onClick={() =>
                          handleDeleteDocument(document.document_id)
                        }
                        disabled={deletingDocumentId === document.document_id}
                      >
                        {deletingDocumentId === document.document_id
                          ? 'Deleting...'
                          : 'Delete'}
                      </button>

                    </div>

                  ))}

                </div>

              )}

            {/* Document Details */}
            {loadingDocumentDetails && (
              <p>Loading document details...</p>
            )}

            {documentDetailsError && (
              <p>{documentDetailsError}</p>
            )}

            {selectedDocumentDetails && (
              <div className="suggestion-card">

                <h3>Document Details</h3>

                <p>
                  Filename: {selectedDocumentDetails.filename}
                </p>

                <p>
                  Document ID: {selectedDocumentDetails.document_id}
                </p>

                <p>
                  Total Chunks: {selectedDocumentDetails.total_chunks}
                </p>

                <p>
                  Total Pages: {selectedDocumentDetails.total_pages}
                </p>

                <button
                  onClick={() => setSelectedDocumentDetails(null)}
                >
                  Close Details
                </button>

              </div>
            )}

          </section>

        )}

        {/* Research History Workspace */}
        {activeView === 'history' && (

          <section className="chat-workspace">

            <div className="welcome-section">

              <div className="welcome-icon">📖</div>

              <h1>Research History</h1>

              <p>
                Your previous research conversations will appear here.
                This feature is coming soon.
              </p>

            </div>

          </section>

        )}

      </main>

    </div>
  );
}

export default App;
