import classNames from "classnames/bind"
import styles from "./Status.module.scss"
import { useTranslation } from "react-i18next";
import { useEffect, useState } from "react";
import { PulseLoader } from "react-spinners";
import { ImBin } from "react-icons/im";
import { IoClose } from "react-icons/io5";
import { readCart, readInvoice, deleteCartItem } from "../../services/api";
import { useCart } from "../../context/CartContext";
import { Link } from "react-router-dom";
const cx = classNames.bind(styles)

const Status = () => {
    const { t } = useTranslation();
    const [loading, setLoading] = useState(true);
    const { cart, setCart } = useCart();
    const cartItems = cart.items || [];
    const [showPaymentModal, setShowPaymentModal] = useState(false);
    const [selectedPaymentMethod, setSelectedPaymentMethod] = useState(null);
    const [showCashConfirmation, setShowCashConfirmation] = useState(false);
    const [orderDetails, setOrderDetails] = useState([]);


    // Tính tổng tiền
    const totalAmount = cartItems.reduce((total, item) => {
        return total + (item.product_price * item.quantity);
    }, 0);

    // Format tiền tệ
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    };

    // Lấy giỏ hàng
    useEffect(() => {
        const fetchInvoice = async () => {
            try {
                const invoice = await readInvoice(); // Gọi API
                const orders = invoice.data.orders || [];
                console.log(invoice)
                // Gộp tất cả order_details từ các đơn hàng
                const allOrderDetails = orders.flatMap(order => order.order_details || []);

                setOrderDetails(allOrderDetails);


            } catch (error) {
                console.error("Lỗi khi lấy hóa đơn:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchInvoice();
    }, []);






    // Xử lý xóa item
    const handleDeleteItem = async (productId) => {
        try {
            await deleteCartItem(productId);
            fetchCart();
        } catch (error) {
            console.error("Lỗi khi xóa sản phẩm:", error);
        }
    };

    // Xử lý đóng modal
    const handleCloseModal = () => {
        setShowPaymentModal(false);
        setSelectedPaymentMethod(null);
        setShowCashConfirmation(false);
    };

    // Xử lý xác nhận thanh toán
    const handleConfirmPayment = () => {
        // Xử lý logic thanh toán ở đây
        console.log("Payment confirmed");
        handleCloseModal();
    };

    // URL QR code (tạm thời)
    const qrCodeUrl = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=example";

    const handlePayment = (method) => {
        setSelectedPaymentMethod(method);
        if (method === "cash") {
            setShowCashConfirmation(true);
        }
    };

    const handleCashConfirm = () => {
        // Xử lý thanh toán tiền mặt
        console.log("Payment method: cash - confirmed");
        setShowCashConfirmation(false);
        setShowPaymentModal(false);
    };

    const handleCloseQR = () => {
        setSelectedPaymentMethod(null);
    };

    return (
        <div className={cx("container")}>
            <div className="row">
                <div className="col-12 text-center mt-3 text-white">
                    <h2 className={cx("", "fw-bold")}>Đơn hàng đã đặt</h2>
                </div>
            </div>

            {loading ? (
                <div className="text-center mt-4">
                    <PulseLoader color="#ffffff" />
                </div>
            ) : orderDetails.length === 0 ? (
                <div className={cx("empty-status")}>
                    <div className={cx("empty-status-content")}>
                        <h3>Quên chưa đặt món rồi nè bạn ơi?</h3>
                        <p>Hãy đặt món để theo dõi trạng thái đơn hàng của bạn</p>
                        <Link to="/menu-order" className={cx("cs-btn-order")}>
                            Đặt món
                        </Link>
                    </div>
                </div>
            ) : (
                <>
                    {orderDetails.map((item, index) => (
                        <div className={cx("order-item")} key={item.product_id}>
                            <img
                                src={item.product_image_url}
                                alt={item.product_name}
                                className={cx("food-image")}
                            />
                            <div className={cx("order-details")}>
                                <h4 className={cx("food-name")}>{item.product_name}</h4>
                                <div className={cx("quantity", "mt-3", "text-white")}>
                                    <span className={cx("quantity-multiplier")}> x {item.quantity}</span>
                                </div>
                            </div>

                            <div className={cx("cs-status", "completed")}>
                                <span className={cx("cs-sub-status")}>chờ xác nhận</span>
                            </div>
                            <span className={cx("cs-deleted")}>
                                <ImBin />
                            </span>
                        </div>
                    ))}

                    <div className="row mt-3 pb-3">
                        <div className="col-6">
                            <button type="button" className={cx("cs-btn-order")}>Gọi thêm món</button>
                        </div>
                        <div className="col-6">
                            <button type="button" className={cx("cs-btn-order")} onClick={() => setShowPaymentModal(true)}>Thanh toán</button>
                        </div>
                    </div>
                </>
            )}

            {/* Payment Modal */}
            {showPaymentModal && (
                <div className={styles['modal-overlay']} onClick={handleCloseModal}>
                    <div className={styles['modal-content']} onClick={e => e.stopPropagation()}>
                        <h2 className={styles['modal-title']}>Chọn phương thức thanh toán</h2>
                        <div className={styles['payment-options']}>
                            <button
                                className={styles['payment-option']}
                                onClick={() => setSelectedPaymentMethod('cash')}
                            >
                                <i className="fas fa-money-bill-wave"></i>
                                Thanh toán tiền mặt
                            </button>
                            <button
                                className={styles['payment-option']}
                                onClick={() => setSelectedPaymentMethod('bank')}
                            >
                                <i className="fas fa-university"></i>
                                Chuyển khoản ngân hàng
                            </button>
                        </div>

                        {selectedPaymentMethod === 'cash' && (
                            <div className={styles['cash-confirmation']}>
                                <h3 className={styles['confirmation-title']}>Xác nhận thanh toán tiền mặt</h3>
                                <div className={styles['confirmation-content']}>
                                    <p className={styles['confirmation-text']}>
                                        Vui lòng chuẩn bị số tiền: {formatCurrency(totalAmount)} để thanh toán khi nhận hàng.
                                    </p>
                                    <div className={styles['confirmation-buttons']}>
                                        <button className={styles['confirm-button']} onClick={handleConfirmPayment}>
                                            Xác nhận
                                        </button>
                                        <button className={styles['cancel-button']} onClick={() => setSelectedPaymentMethod(null)}>
                                            Hủy
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}

                        {selectedPaymentMethod === 'bank' && (
                            <div className={styles['qr-section']}>
                                <div className={styles['qr-title']}>
                                    Quét mã QR để thanh toán
                                    <button className={styles['qr-close']} onClick={handleCloseQR}>
                                        <IoClose />
                                    </button>
                                </div>
                                <div className={styles['qr-container']}>
                                    <img src={qrCodeUrl} alt="QR Code" className={styles['qr-code']} />
                                </div>
                                <p className={styles['qr-instruction']}>
                                    Vui lòng quét mã QR bằng ứng dụng ngân hàng để thanh toán
                                </p>
                            </div>
                        )}

                        {!selectedPaymentMethod && (
                            <button className={styles['close-modal']} onClick={handleCloseModal}>
                                Đóng
                            </button>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Status;
