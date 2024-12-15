import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import { Menu, FileText, MessageSquare } from "lucide-react";
import { Link, useNavigate } from "react-router";
import toast from "react-hot-toast";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import { useTheme } from "@mui/material/styles";
import { initialState } from "@ant-design/pro-chat/es/ProChat/store/initialState";

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`full-width-tabpanel-${index}`}
      aria-labelledby={`full-width-tab-${index}`}
      {...other}
    >
      {children}
    </div>
  );
}

const intialState = {
  email: "",
  password: "",
  confirmPassword: "",
};

const NavBar = ({
  toggleSidebar,
  onSearchClick,
  onNotificationsClick,
  onProfileClick,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState(intialState);
  const [selectedModel, setSelectedModel] = useState("llama3.2");
  const [tabId, setTabId] = React.useState(0);
  const theme = useTheme();
  const navigate = useNavigate();

  useEffect(() => {
    const storedModel = localStorage.getItem("selectedModel") || "llama3.2";
    setSelectedModel(storedModel);
    localStorage.setItem("selectedModel", storedModel);
  }, []);

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const logoutUser = (e) => {
    localStorage.removeItem("token");
    localStorage.removeItem("summary");
    navigate("/");
  };

  const handleModelChange = (e) => {
    const newModel = e.target.value;
    setSelectedModel(newModel);
    localStorage.setItem("selectedModel", newModel);
  };

  const handleChange = (event, newValue) => {
    setTabId(newValue);
  };

  function a11yProps(index) {
    return {
      id: `full-width-tab-${index}`,
      "aria-controls": `full-width-tabpanel-${index}`,
    };
  }

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(
        "https://research-llm-backend-316797979759.us-east4.run.app/login",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
          }),
        }
      );

      if (!response.ok) {
        const { error } = await response.json();
        throw new Error(error || "Login failed");
      }

      const data = await response.json();
      localStorage.removeItem("summary");
      localStorage.setItem("token", data.token);
      toast.success(data.message || "Login successful!");
      setFormData(initialState);
      window.location.reload();
      closeModal();
    } catch (error) {
      toast.error(error.message || "An error occurred during login.");
      setFormData(initialState);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error("Passwords do not match!");
      return;
    }

    try {
      const response = await fetch(
        "https://research-llm-backend-316797979759.us-east4.run.app/register",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
          }),
        }
      );

      if (!response.ok) {
        const { error } = await response.json();
        throw new Error(error || "Registration failed");
      }

      const data = await response.json();
      toast.success(data.message || "Registration successful!");
      setFormData(initialState);
      closeModal();
    } catch (error) {
      toast.error(error.message || "An error occurred during registration.");
      setFormData(initialState);
    }
  };

  return (
    <>
      <div className="h-14 flex items-center px-4 border-b border-zinc-800 bg-zinc-900">
        {/* Left Section */}
        <div className="flex items-center gap-4">
          {toggleSidebar && (
            <button
              onClick={toggleSidebar}
              className="hover:bg-zinc-800 rounded p-1"
            >
              <Menu className="w-6 h-6 text-gray-300" />
            </button>
          )}
          <h1 className="text-lg font-semibold text-gray-300">
            <Link to="/search" className="hover:text-gray-200 text-gray-300">
              Research Paper Summarizer
            </Link>
          </h1>
        </div>

        {/* Right Section */}
        <div className="ml-auto flex items-center gap-4">
          <select
            value={selectedModel}
            onChange={handleModelChange}
            className="bg-zinc-900 text-gray-300 border border-zinc-700 rounded p-2"
          >
            <option value="llama3.2">llama3.2</option>
            <option value="llama3.3">llama3.3</option>
            <option value="gemini1.5">gemini1.5</option>
          </select>

          <Link to="/search" className="hover:text-gray-200 text-gray-300">
            <FileText className="inline-block w-5 h-5 mr-1" />
            Query
          </Link>
          {localStorage.getItem("token") ? (
            <Link to="/notebook" className="hover:text-gray-200 text-gray-300">
              <MessageSquare className="inline-block w-5 h-5 mr-1" />
              Chat
            </Link>
          ) : (
            <></>
          )}

          {localStorage.getItem("token") ? (
            <button
              onClick={logoutUser}
              className="hover:bg-zinc-800 rounded p-2 text-gray-300"
            >
              Logout
            </button>
          ) : (
            <button
              onClick={openModal}
              className="hover:bg-zinc-800 rounded p-2 text-gray-300"
            >
              Login
            </button>
          )}
        </div>
      </div>

      {/* Modal */}
      {isModalOpen &&
        ReactDOM.createPortal(
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div className="bg-zinc-800 text-gray-300 p-6 rounded-md shadow-lg w-96">
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <Tabs value={tabId} onChange={handleChange} textColor="white">
                  <Tab label="Login" {...a11yProps(0)} />
                  <Tab label="Register" {...a11yProps(1)} />
                </Tabs>
                <button
                  onClick={closeModal}
                  className="text-gray-300 hover:underline"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="25"
                    height="25"
                    viewBox="0 0 24 24"
                    fill="#FFFFFF"
                  >
                    <path d="M 4.7070312 3.2929688 L 3.2929688 4.7070312 L 10.585938 12 L 3.2929688 19.292969 L 4.7070312 20.707031 L 12 13.414062 L 19.292969 20.707031 L 20.707031 19.292969 L 13.414062 12 L 20.707031 4.7070312 L 19.292969 3.2929688 L 12 10.585938 L 4.7070312 3.2929688 z"></path>
                  </svg>
                </button>
              </div>

              <TabPanel value={tabId} index={0} dir={theme.direction}>
                <form
                  onSubmit={handleLogin}
                  className="flex flex-col gap-4 mt-4"
                >
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="Email"
                    className="bg-zinc-900 text-gray-300 border border-zinc-700 rounded p-2"
                    required
                  />
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Password"
                    className="bg-zinc-900 text-gray-300 border border-zinc-700 rounded p-2"
                    required
                  />
                  <button
                    type="submit"
                    className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
                  >
                    Submit
                  </button>
                </form>
              </TabPanel>

              <TabPanel value={tabId} index={1} dir={theme.direction}>
                <form
                  onSubmit={handleRegister}
                  className="flex flex-col gap-4 mt-4"
                >
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="Email"
                    className="bg-zinc-900 text-gray-300 border border-zinc-700 rounded p-2"
                    required
                  />
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Password"
                    className="bg-zinc-900 text-gray-300 border border-zinc-700 rounded p-2"
                    required
                  />
                  <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    placeholder="Confirm Password"
                    className="bg-zinc-900 text-gray-300 border border-zinc-700 rounded p-2"
                    required
                  />
                  <button
                    type="submit"
                    className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
                  >
                    Submit
                  </button>
                </form>
              </TabPanel>
            </div>
          </div>,
          document.getElementById("login")
        )}
    </>
  );
};

export default NavBar;
