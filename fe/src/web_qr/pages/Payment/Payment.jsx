import React, { useContext, useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { SocketContext } from "../../../main/context/SocketContext";
import { endSession, fetchAwaitPaymentStatus } from "../../services/api";
import { IoClose } from "react-icons/io5";
import { FaStar } from "react-icons/fa";
import styles from "./Payment.module.scss";
import { useTranslation } from "react-i18next";
import CallStaffButton from "../../components/CallStaffButton/CallStaffButton";
// import { toast } from "react-toastify"; // Uncomment if you use toast notifications

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const { t } = useTranslation();
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [session, setSession] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const socket = useContext(SocketContext);
  const navigate = useNavigate();
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [feedback, setFeedback] = useState("");

  // Fetch payment status on mount
  useEffect(() => {
    const sendResultToBackend = async () => {
      try {
        const params = Object.fromEntries(searchParams.entries());
        const response = await fetchAwaitPaymentStatus(params);
        const status = response?.data?.status;
        const sessionData = response?.data?.session;

        setPaymentStatus(status);
        setSession(sessionData);

        // Notify via socket if payment is successful
        if (socket && socket.readyState === WebSocket.OPEN) {
          socket.send(
            JSON.stringify({
              type: "payment",
              session: sessionData,
            })
          );
          setShowModal(true);
        }
      } catch (error) {
        console.error("Error sending payment result to server:", error);
        setPaymentStatus("fail");
      }
    };

    sendResultToBackend();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, socket]);

  // Handle closing modal and ending session
  const handleClose = async () => {
    setShowModal(false);
    const response = await endSession();
    const status = response?.status;

    if (status === 200) {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(
          JSON.stringify({
            type: "session",
            session,
          })
        );
      }
      navigate("/menu-order");
    }
  };

  // Handle closing the rating modal
  const handleCloseRating = () => {
    setRating(0);
    setFeedback("");
  };

  // Handle submitting the rating
  const handleSubmitRating = () => {
    if (rating === 0) {
      // toast.warning(t("status_order.rating_warning"));
      return;
    }
    // toast.success(t("status_order.rating_success"));
    setRating(0);
    setFeedback("");
  };

  return (
    <div className={styles.container}>
      <div className={styles["modal-overlay"]} onClick={handleCloseRating}>
        <div
          className={styles["modal-content"]}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            className={styles["close-rating"]}
            onClick={handleCloseRating}
          >
            <IoClose />
          </button>
          <div className={styles["modal-header"]}>
            <h2 className={styles["modal-title"]}>
              {t("status_order.rating_title")}
            </h2>
          </div>
          <div className={styles["rating-section"]}>
            <div className={styles["star-rating"]}>
              {[...Array(5)].map((_, index) => {
                const ratingValue = index + 1;
                return (
                  <label key={index}>
                    <input
                      type="radio"
                      name="rating"
                      value={ratingValue}
                      onClick={() => setRating(ratingValue)}
                    />
                    <FaStar
                      className={styles["star"]}
                      color={
                        ratingValue <= (hover || rating)
                          ? "#ffc107"
                          : "#e4e5e9"
                      }
                      size={40}
                      onMouseEnter={() => setHover(ratingValue)}
                      onMouseLeave={() => setHover(0)}
                    />
                  </label>
                );
              })}
            </div>
            <textarea
              className={styles["feedback-input"]}
              placeholder={t("status_order.feedback_placeholder")}
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
            <button
              className={styles["submit-rating"]}
              onClick={handleSubmitRating}
            >
              {t("status_order.submit_rating")}
            </button>
          </div>
        </div>
      </div>
      <CallStaffButton />
    </div>
  );
};

export default PaymentSuccess;
