import React, { useState } from "react";
import NavBar from "../navbar";

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

const SearchingComponent = () => {
  const [searchText, setSearchText] = useState("");
  const [resultText, setResultText] = useState(
    "Your summarized text will appear here..."
  );
  const [dynamoData, setDynamoData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const selectedModel = localStorage.getItem("selectedModel");
      const payload = {
        query: searchText,
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
      setResultText(data.answer || "No results found.");
      setDynamoData(data.dynamo_data || []); // Extract and set dynamo_data
      setIsLoading(false);
    } catch (error) {
      setResultText(`Error: ${error.message}`);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-zinc-900 text-gray-300">
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <NavBar />

        {/* Content Area */}
        <div className="flex-1 relative p-6" style={{ background: "#18181b" }}>
          {/* Dot Pattern */}
          <DotPattern />

          {/* Search and Results Section */}
          <div className="relative flex flex-col items-center gap-6 mt-8 mx-auto w-full max-w-3xl">
            {/* Search Section */}
            <form
              onSubmit={handleSearch}
              className="flex items-center bg-zinc-800 p-4 rounded-lg shadow-md w-full"
            >
              <input
                type="text"
                placeholder="Enter your query here..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                className="flex-1 px-4 py-2 text-sm text-gray-300 bg-transparent focus:outline-none"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded-md"
                disabled={searchText?.length ? false : true}
              >
                {isLoading ? "Loading" : "Search"}
              </button>
            </form>

            {/* Results Block */}
            <div className="bg-zinc-800 p-6 rounded-lg shadow-md w-full">
              <h2 className="text-lg font-semibold mb-4">Results</h2>
              <p className="text-sm text-gray-400">{resultText}</p>
            </div>

            {/* Dynamo Data Cards */}
            <div className="w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {dynamoData.map((item, index) => (
                <div
                  key={index}
                  className="bg-zinc-800 p-4 rounded-lg shadow-md flex flex-col items-start"
                >
                  <h3 className="text-md font-semibold mb-2 text-white">
                    {item.PaperPDFName.split(".")[0]}
                  </h3>
                  <p className="text-sm text-gray-400 mb-2">
                    Paper ID: {item.PaperID}
                  </p>
                  <a
                    href={item.PaperLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-indigo-400 hover:underline text-sm"
                  >
                    View PDF
                  </a>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SearchingComponent;
