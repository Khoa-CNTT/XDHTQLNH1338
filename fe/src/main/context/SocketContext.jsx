import { createContext, useEffect, useState } from "react";
import Cookies from "js-cookie";
import { endSession } from "../../web_qr/services/api";
export const SocketContext = createContext(null);

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);

  // Function to handle session ending
  async function asyncEndSession() {
    try {
      const response = await endSession();
      if (response.status === 200) {
        console.log("✅ End session thành công");
        window.location.href = "/";
      } else {
        console.error("⚠️ End session failed:", response);
      }
    } catch (err) {
      console.error("❌ Error ending session:", err);
    }
  }

  // Set up socket connection on mount
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:5001/ws/notifications/order/");

    ws.onopen = () => {
      console.log("✅ WebSocket connected!");
    };

    ws.onclose = (event) => {
      console.log("❌ WebSocket disconnected!", event);
    };

    ws.onerror = (error) => {
      console.error("⚠️ WebSocket error:", error);
    };

    setSocket(ws);

    // Cleanup on unmount
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  // Handle socket.onmessage separately (reactive to socket changes)
  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("📩 WebSocket message received:", data);

        if (data?.type === "end_session") {
          asyncEndSession();
        }

        // Add more message type handling here if needed

      } catch (err) {
        console.error("❌ Error parsing WebSocket message:", err);
      }
    };

    socket.addEventListener("message", handleMessage);

    return () => {
      socket.removeEventListener("message", handleMessage);
    };
  }, [socket]);

  return (
    <SocketContext.Provider value={socket}>
      {children}
    </SocketContext.Provider>
  );
};
