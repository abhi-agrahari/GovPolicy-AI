import { useEffect, useRef, useState } from "react";
import { authApi, documentApi, chatApi } from "../api";
import "./Home.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function Home() {
  const [user, setUser] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [file, setFile] = useState(null);
  const [addingFile, setAddingFile] = useState(false);
  const [message, setMessage] = useState("");
  const [url, setUrl] = useState("");
  const [addingUrl, setAddingUrl] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);
  const chatMessagesRef = useRef(null);
  const [showKnowledgeDialog, setShowKnowledgeDialog] = useState(false);

  useEffect(() => {
    loadUser();
    loadDocuments();
  }, []);

  useEffect(() => {
    const chat = chatMessagesRef.current;

    if (chat && !asking) {
      chat.scrollBy({
        top: 150,
        behavior: "smooth",
      });
    }
  }, [messages, asking]);

  // load current user and documents
  const loadUser = async () => {
    const data = await authApi.getCurrentUser();
    setUser(data);
  };

  const loadDocuments = async () => {
    const data = await documentApi.getDocuments();
    setDocuments(data.documents);
  };

  // upload PDF functionality
  const uploadFile = async () => {
    if (!file) {
      setMessage("Please select a PDF.");
      return;
    }

    setAddingFile(true);

    try {
      const data = await documentApi.upload(file);

      setMessage(data.message);
      setFile(null);

      document.getElementById("pdf-input").value = "";

      loadDocuments();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setAddingFile(false);
    }
  };

  // add website functionality
  const addWebsite = async () => {
    if (!url.trim()) {
      setMessage("Please enter a website URL.");
      return;
    }

    try {
      new URL(url);
    } catch {
      setMessage("Please enter a valid URL.");
      return;
    }

    setAddingUrl(true);
    setMessage("");

    try {
      const data = await documentApi.addWebsite(url);

      setMessage(data.message);
      setUrl("");

      await loadDocuments();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setAddingUrl(false);
    }
  };

  const deleteDocument = async (id) => {
    await documentApi.deleteDocument(id);
    loadDocuments();
  };

  const logout = async () => {
    await authApi.logout();
    window.location.reload();
  };

  // chat functionality
  const askQuestion = async () => {
    if (!question.trim() || asking) return;

    const userQuestion = question.trim();

    setMessages((current) => [
      ...current,
      { role: "user", text: userQuestion },
    ]);

    setQuestion("");
    setAsking(true);

    try {
      const data = await chatApi.ask(userQuestion);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: `Error: ${error.message}`,
          sources: [],
        },
      ]);
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="home">

      <header className="navbar">
        <h2>GovPolicy AI</h2>

        <div className="navbar-left">
          <span>{user?.email}</span>
          <button className="logout-button" onClick={logout}>Logout</button>
        </div>
      </header>

      <main>

        <div className="header">
          <h1>Government Policy Assistant</h1>

          <button onClick={() => setShowKnowledgeDialog(true)}>
            Add or Remove Knowledge
          </button>
        </div>

        <p className="subtitle">
          Upload policy documents or Paste URL and ask questions using AI.
        </p>

        {/* Add Knowledge button opens this dialog */}
        {showKnowledgeDialog && (
          <div
            className="modal-overlay"
            onClick={() => setShowKnowledgeDialog(false)}
          >
            <div
              className="knowledge-modal"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-header">
                <h2>Add Knowledge</h2>
                {message && <p className="message">{message}</p>}
                <button
                  className="close-modal"
                  onClick={() => setShowKnowledgeDialog(false)}
                >
                  ✕
                </button>
              </div>

              {/* Upload PDF */}
              <section className="card">
                <h2>Upload PDF</h2>

                <input
                  id="pdf-input"
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setFile(e.target.files[0])}
                />

                <button onClick={uploadFile} disabled={addingFile}>
                  {addingFile ? "Processing..." : "Upload"}
                </button>

                {file && <p>Selected: {file.name}</p>}
              </section>

              {/* Website URL */}
              <section className="card">
                <h2>Add Website</h2>

                <p>Enter a government policy webpage URL.</p>

                <input
                  type="text"
                  placeholder="https://example.gov.in/policy"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />

                <button onClick={addWebsite} disabled={addingUrl}>
                  {addingUrl ? "Processing..." : "Add Website"}
                </button>
              </section>

              {/* Documents */}
              <section className="card">
                <h2>My Documents</h2>

                {documents.length === 0 ? (
                  <p>No documents yet.</p>
                ) : (
                  documents.map((document) => (
                    <div className="document" key={document.document_id}>
                      <span>{document.filename}</span>

                      <button
                        className="delete-button"
                        onClick={() =>
                          deleteDocument(document.document_id)
                        }
                      >
                        Delete
                      </button>
                    </div>
                  ))
                )}
              </section>
            </div>
          </div>
        )}

        {/* Chat Section */}
        <section className="card chat-section">
          <div className="chat-messages" ref={chatMessagesRef}>
            {messages.length === 0 && (
              <p className="chat-empty">
                Your conversation will appear here.
              </p>
            )}

            {messages.map((message, index) => (
              <div className="chat-message" key={index}>
                <strong>
                  {message.role === "user" ? "" : "GovPolicy AI"}
                </strong>

                <div className="message-content">
                  {message.role === "assistant" ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.text}
                    </ReactMarkdown>
                  ) : (
                    <p><strong>You: </strong>{message.text}</p>
                  )}
                </div>

                {message.sources?.length > 0 && (
                  <div className="sources">
                    <strong>Sources</strong>

                    {message.sources.map((source, sourceIndex) => (
                      <p key={sourceIndex}>
                        {source.filename} — Page {source.page}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {asking && <p className="chat-empty">Thinking...</p>}
          </div>

          <div className="chat-input">
            <textarea
              placeholder="Ask a question..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  askQuestion();
                }
              }}
            />

            <button onClick={askQuestion} disabled={asking || !question.trim()}>
              {asking ? "Asking..." : "Ask"}
            </button>
          </div>
        </section>

      </main>

    </div>
  );
}

export default Home;