import { createContext, useEffect, useState } from "react";

export const SocketContext = createContext(null);

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const ws = new WebSocket("ws://0.0.0.0:5001/ws/notifications/order/");

    // ws.onopen = () => {
    //   console.warn("WebSocket connection established")
    // }

    // ws.onmessage = (event) => {
    //   const data = JSON.parse(event.data)
    //   console.info("Received data: ", data)
    // }

    // ws.onclose = () => {
    //   console.warn("WebSocket connection closed")
    // }

    // ws.onerror = (error) => {
    //   console.error("WebSocket error: ", error)
    // }

    setSocket(ws);

    return () => {
      if (ws) {
        // ws.close()
        // console.warn("WebSocket connection closed on component unmount")
      }
    };
  }, []);

  return (
    <SocketContext.Provider value={socket}>{children}</SocketContext.Provider>
  );
};
