import { endSession, fetchAwaitPaymentStatus } from "../../services/api";
import React, { useContext, useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { SocketContext } from "../../../main/context/SocketContext";
import { Modal, Button } from "react-bootstrap";

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [session, setSession] = useState(null);
  const [showModal, setShowModal] = useState(false); // state to control modal visibility
  const socket = useContext(SocketContext);
  const navigate = useNavigate();
  useEffect(() => {
    const sendResultToBackend = async () => {
      try {
        const params = Object.fromEntries(searchParams.entries());
        const response = await fetchAwaitPaymentStatus(params);

        const status = response?.data?.status;
        const session = response?.data?.session;

        setPaymentStatus(status);
        setSession(session);

        // Gửi socket nếu thanh toán thành công
        if (
          socket &&
          socket.readyState === WebSocket.OPEN
        ) {
          socket.send(
            JSON.stringify({
              type: "payment",
              session: session,
            })
          );
          setShowModal(true); // Show modal on success
        }
      } catch (error) {
        console.error("Lỗi khi gửi kết quả thanh toán về server:", error);
        setPaymentStatus("fail");
      }
    };

    sendResultToBackend();
  }, [searchParams, socket]);

  const handleClose = async () => {
    setShowModal(false); // Close modal
    const response = await endSession();
    let status = response?.status 

    if(status == 200) {
      if (
        socket &&
        socket.readyState === WebSocket.OPEN
      ) {
        socket.send(
          JSON.stringify({
            type: "session",
            session: session,
          })
        );
      }
      navigate('/menu-order');
    }else {

    }
  };

  return (
    <div>
      {/* Bootstrap Modal */}
      <Modal show={showModal} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>Thông báo</Modal.Title>
        </Modal.Header>
        <Modal.Body>Bạn đã thanh toán thành công.</Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Kết thúc phiên đăng nhập
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default PaymentSuccess;
