
import { fetchAwaitPaymentStatus } from '../../services/api';
import React, { useContext, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { SocketContext } from '../../../main/context/SocketContext';

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const socket = useContext(SocketContext);

  useEffect(() => {
    const sendResultToBackend = async () => {
      try {
        const params = Object.fromEntries(searchParams.entries());
        const response = await fetchAwaitPaymentStatus(params);

        const status = response?.data?.status;
        const session = response?.data?.session;

        setPaymentStatus(status);
        setSessionId(session);

        // Gửi socket nếu thanh toán thành công
        if (status === 'success' && socket && socket.readyState === WebSocket.OPEN) {
          socket.send(
            JSON.stringify({
              type: "payment",
              session: session,
            })
          );
        }

      } catch (error) {
        console.error("Lỗi khi gửi kết quả thanh toán về server:", error);
        setPaymentStatus("fail");
      }
    };

    sendResultToBackend();
  }, [searchParams, socket]);

  return (
    <div>
      {paymentStatus === 'success' ? (
        <h1>✅ Thanh toán thành công!</h1>
      ) : paymentStatus === 'fail' ? (
        <h1>❌ Thanh toán thất bại. Vui lòng thử lại.</h1>
      ) : (
        <h1>⏳ Đang xử lý thanh toán...</h1>
      )}
    </div>
  );
};

export default PaymentSuccess;

