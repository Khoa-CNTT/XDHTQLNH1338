import { createContext, useEffect, useState } from "react";
import Cookies from "js-cookie";
export const SocketContext = createContext(null);

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);

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

    ws.onmessage = (event) => {
      console.log("📩 WebSocket message received:", event.data);
      var data = JSON.parse(event.data);
      if (data?.type === "end_session") {
        Cookies.remove("token");
        // hoặc redirect
        window.location.href = "/";
      }
    };

    setSocket(ws);

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  return (
    <SocketContext.Provider value={socket}>{children}</SocketContext.Provider>
  );
};
