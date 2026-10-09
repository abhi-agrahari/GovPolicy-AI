import { useEffect, useState } from "react";
import { authApi, documentApi } from "../api";
import "./Home.css";

function Home() {
  const [user, setUser] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadUser();
    loadDocuments();
  }, []);

  const loadUser = async () => {
    const data = await authApi.getCurrentUser();
    setUser(data);
  };

  const loadDocuments = async () => {
    const data = await documentApi.getDocuments();
    setDocuments(data.documents);
  };

  const uploadFile = async () => {
    if (!file) {
      setMessage("Please select a PDF.");
      return;
    }

    try {
      const data = await documentApi.upload(file);

      setMessage(data.message);
      setFile(null);

      document.getElementById("pdf-input").value = "";

      loadDocuments();
    } catch (error) {
      setMessage(error.message);
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

  return (
    <div className="home">

      <header className="navbar">
        <h2>GovPolicy AI</h2>

        <div>
          <span>{user?.email}</span>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      <main>

        <h1>Government Policy Assistant</h1>

        <p className="subtitle">
          Upload policy documents or Paste URL and ask questions using AI.
        </p>

        {/* Upload PDF */}
        <section className="card">
          <h2>Upload PDF</h2>

          <input
            id="pdf-input"
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
          />

          <button onClick={uploadFile}>
            Upload
          </button>

          {file && <p>Selected: {file.name}</p>}
          {message && <p>{message}</p>}
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

      </main>

    </div>
  );
}

export default Home;