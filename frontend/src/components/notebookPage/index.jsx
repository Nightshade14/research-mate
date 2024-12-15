import React, { useEffect, useState } from "react";
import { Menu, FileText } from "lucide-react";
import NavBar from "../navbar";
import toast from "react-hot-toast";
import { ProChat } from "@ant-design/pro-chat";
import Modal from "react-modal";

const DotPattern = () => (
  <svg className="absolute w-full h-full" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <pattern
        id="dot-pattern"
        x="0"
        y="0"
        width="20"
        height="20"
        patternUnits="userSpaceOnUse"
      >
        <circle
          cx="2"
          cy="2"
          r="1"
          fill="currentColor"
          className="text-zinc-800"
        />
      </pattern>
    </defs>
    <rect width="100%" height="100%" fill="url(#dot-pattern)" />
  </svg>
);

const NotebookInterface = () => {
  const [sources, setSources] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [selectedSourceId, setSelectedSourceId] = useState(null);
  const [searchText, setSearchText] = useState("");
  const [searchResult, setResultText] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Fetch papers from the backend
  const fetchPapers = async () => {
    const token = localStorage.getItem("token"); // Replace this with the actual user UUID
    try {
      const response = await fetch(
        "https://research-llm-backend-316797979759.us-east4.run.app/getPapers",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ token: token }), // Send the UUID in the request body
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch papers");
      }

      const data = await response.json();
      setSources(data); // Update sources with the fetched data
    } catch (error) {
      console.error("Error fetching papers:", error.message);
    }
  };

  useEffect(() => {
    fetchPapers(); // Fetch papers when the component mounts
  }, []);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const selectSource = (sourceId) => {
    setSelectedSourceId(sourceId === selectedSourceId ? null : sourceId);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      const formData = new FormData();
      formData.append("file", file);
      const token = localStorage.getItem("token"); // Adjust the key based on where your token is stored
      if (token) {
        formData.append("token", token);
      }

      // Replace this with your file upload API endpoint
      const response = await fetch(
        "https://research-llm-backend-316797979759.us-east4.run.app/summarize",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("File upload failed");
      }

      const data = await response.json();
      // Add the uploaded file to the sources list
      const newSource = {
        name: file.name,
        type: file.type,
        id: sources.length + 1,
      };
      setSources([...sources, newSource]);
      setSearchText("");
      setResultText(data.message || "No summary available.");
      localStorage.setItem("summary", data.message);
      toast.success("File uploaded successfully!");
    } catch (error) {
      console.error("Upload error:", error);
      toast.error(`Error: ${error.message}`);
    }
  };

  const handleSummary = async (e) => {};

  const handleSearch = async (message) => {
    // e.preventDefault();

    const selectedSource = sources.find(
      (source) => source.id === selectedSourceId
    );
    if (!selectedSource) {
      toast("Please select a source to summarize.", {
        icon: "⚠️",
      });
      return;
    }

    const selectedModel = localStorage.getItem("selectedModel") || "llama3.2";

    try {
      const payload = {
        file_id: selectedSource.id, // Use the file ID
        query: message[message.length - 1]["message"],
        model: selectedModel, // Use the selected model
      };

      const response = await fetch(
        "https://research-llm-backend-316797979759.us-east4.run.app/query",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch results. Please try again.");
      }

      const data = await response.json();
      toast.success("Query fetched successfully!");
      setSearchText("");
      // setResultText(data.summary || "No summary available.");
      return data.answer;
    } catch (error) {
      toast.error(`Error: ${error.message}`);
    }
  };

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  return (
    <>
      <style type="text/css">
        {`
            .css-dev-only-do-not-override-142vneq, .ant-app{
                height: auto;
                max-height: 100vh;
                width: 100%;
                overflow-y: auto;
                position: relative;
                box-sizing: border-box;
            }
            
            .ant-pro-chat-chat-list-container{
                height: 700px !important;
            }
            .ant-pro-chat-input-area{
                background: #18181b;
                padding-top: 0px;
            }
            .anticon{
                color: white;
            }
            p{
              color: white !important;
            }        
            .ant-pro-chat-list-item-message-content{
              background-color: #4b4c4c;
            }
            .ant-input, .ant-input:focus, .ant-input:hover{
              color: white;
              background: #4b4c4c;
            }
            .ant-select-selection__placeholder{
              color : white;
            }
            span.ant-select-selection-placeholder{
              color: white !important;
            }
            .ReactModal__Content{
              max-height:60%;
              overflow-y: scroll;
            }
        `}
      </style>
      <div className="flex h-screen bg-zinc-900 text-gray-300">
        {/* Sidebar */}
        <div
          className={`
          ${isSidebarOpen ? "w-64" : "w-16"} 
          flex-shrink-0 transition-all duration-300 ease-in-out 
          border-r border-zinc-800 flex flex-col bg-zinc-900
        `}
        >
          <div className="h-14 flex items-center px-4 border-b border-zinc-800">
            <div className="flex items-center gap-2">
              <button
                onClick={toggleSidebar}
                className="hover:bg-zinc-800 rounded p-1"
              >
                <Menu className="w-6 h-6" />
              </button>
            </div>
          </div>

          {isSidebarOpen ? (
            <div
              className="p-4 border-b border-zinc-800"
              style={{ borderBottom: "none" }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 flex items-center justify-center rounded-full border border-zinc-700">
                    {sources.length}
                  </div>
                  <span>Sources</span>
                </div>
                <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-zinc-800 border border-zinc-700">
                  <label htmlFor="file-upload" className="text-lg">
                    +
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </button>
              </div>

              {sources.map((source) => (
                <div
                  key={source.id}
                  className="flex items-center justify-between py-2 px-3 text-sm hover:bg-zinc-800/50 rounded cursor-pointer"
                  onClick={() => selectSource(source.id)}
                  role="radio"
                  aria-checked={selectedSourceId === source.id}
                >
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-red-500" />
                    <span>{source.name}</span>
                  </div>
                  <div className="relative flex items-center">
                    <div
                      className={`
                    w-4 h-4 rounded-full border
                    ${
                      selectedSourceId === source.id
                        ? "border-blue-500 bg-blue-500"
                        : "border-zinc-600"
                    }
                    transition-colors duration-200
                  `}
                    >
                      {selectedSourceId === source.id && (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center pt-4 gap-4">
              <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-zinc-800 border border-zinc-700">
                <span className="text-lg">+</span>
              </button>
              <div className="w-6 h-6 flex items-center justify-center rounded-full border border-zinc-700 text-sm">
                {sources.length}
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          <NavBar />
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              marginTop: "10px",
            }}
          >
            <button
              style={{ width: "30vw" }}
              onClick={openModal}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Summary
            </button>
          </div>
          <Modal
            isOpen={isModalOpen}
            onRequestClose={closeModal}
            contentLabel="Example Modal"
            className="bg-zinc-800 text-gray-300 p-6 rounded-md shadow-lg max-w-lg mx-auto mt-20"
            overlayClassName="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
          >
            <h2 className="text-lg font-semibold mb-4">Summary</h2>
            <p className="mb-4">{localStorage.getItem("summary")}</p>
            <button
              onClick={closeModal}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Close
            </button>
          </Modal>
          <ProChat
            className="h-50"
            locale="en-US"
            helloMessage={<div style={{ color: "white" }}>{searchResult}</div>}
            request={async (messages) => {
              const text = await handleSearch(messages);
              console.log("ANSWER:", text);

              return new Response(text);
            }}
            style={{ height: "100vh" }}
          />
        </div>
      </div>
    </>
  );
};

export default NotebookInterface;
