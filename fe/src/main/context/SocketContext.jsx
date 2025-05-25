import { createContext, useEffect, useState } from "react";
import { endSession } from "../../web_qr/services/api";

// Create a context for the socket
export const SocketContext = createContext(null);

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);

  // Ends the session and redirects the user
  const asyncEndSession = async () => {
    try {
      const response = await endSession();
      if (response.status === 200) {
        console.log("✅ End session thành công");
        window.location.href = "/thank-you";
      } else {
        console.error("⚠️ End session failed:", response);
      }
    } catch (err) {
      console.error("❌ Error ending session:", err);
    }
  };

  // Initialize WebSocket connection on mount
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:5001/ws/notifications/order/");

    ws.onopen = () => console.log("✅ WebSocket connected!");
    ws.onclose = (event) => console.log("❌ WebSocket disconnected!", event);
    ws.onerror = (error) => console.error("⚠️ WebSocket error:", error);

    setSocket(ws);

    // Cleanup WebSocket on unmount
    return () => {
      ws.close();
    };
  }, []);

  // Listen for messages from the WebSocket
  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("📩 WebSocket message received:", data);

        if (data?.type === "end_session") {
          asyncEndSession();
        }
        // Handle other message types here if needed
      } catch (err) {
        console.error("❌ Error parsing WebSocket message:", err);
      }
    };

    socket.addEventListener("message", handleMessage);

    // Cleanup event listener on unmount or socket change
    return () => {
      socket.removeEventListener("message", handleMessage);
    };
  }, [socket]);

  return (
    <SocketContext.Provider value={socket}>{children}</SocketContext.Provider>
  );
};
