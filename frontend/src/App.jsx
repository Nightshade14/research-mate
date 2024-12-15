import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router";

import NotebookPage from "./components/notebookPage";
import SearchingComponent from "./components/searchPage/Index";
import { Toaster } from "react-hot-toast";

import "./index.css";

function App() {
  return (
    <BrowserRouter>
      <Toaster />
      <Routes>
        <Route path="/" element={<Navigate to="/search" />} />
        <Route path="/search" element={<SearchingComponent />} />
        <Route path="/notebook" element={<NotebookPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
