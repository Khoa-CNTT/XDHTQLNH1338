import classNames from "classnames/bind";
import styles from "./Order.module.scss";
import { useTranslation } from "react-i18next";
import { useEffect, useState } from "react";
import { PulseLoader } from "react-spinners";
import { ImBin } from "react-icons/im";
import { readCart, updateQuantityCart, createInvoice } from "../../services/api";
import { useCart } from "../../context/CartContext";
import { toast } from 'react-toastify';
import { useNavigate } from "react-router-dom";
import config from "../../config";
import { FaArrowLeft } from "react-icons/fa";



const cx = classNames.bind(styles);

const Order = () => {
    const { t } = useTranslation();
    const [loading, setLoading] = useState(true);
    const { cart, setCart } = useCart();
    const cartItems = cart.items || [];
    const navigate = useNavigate()

    const fetchCart = async () => {
        setLoading(true);
        try {
            const response = await readCart();
            if (response.data && Array.isArray(response.data.items)) {
                setCart(response.data);
            } else {
                setCart({ items: [] });
            }
        } catch (error) {
            toast.error("Lỗi khi lấy giỏ hàng:", error);
            setCart({ items: [] });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchCart(); }, []);

    // Tăng số lượng sản phẩm
    const handleIncreaseQuantity = async (product_id, currentQuantity) => {
        try {
            await updateQuantityCart({ product_id, quantity: currentQuantity + 1 });

            setCart((prevCart) => {
                const updatedItems = prevCart.items.map((item) =>
                    item.product === product_id ? { ...item, quantity: item.quantity + 1 } : item
                );
                return { ...prevCart, items: updatedItems };
            });
        } catch (error) {
            toast.error("Lỗi khi tăng số lượng:", error);
        }
    };

    const handleDecreaseQuantity = async (product_id, currentQuantity) => {
        if (currentQuantity <= 1) return;

        try {
            await updateQuantityCart({ product_id, quantity: currentQuantity - 1 });

            setCart((prevCart) => {
                const updatedItems = prevCart.items.map((item) =>
                    item.product === product_id ? { ...item, quantity: item.quantity - 1 } : item
                );
                return { ...prevCart, items: updatedItems };
            });
        } catch (error) {
            toast.error("Lỗi khi giảm số lượng:", error);
        }
    };

    // Xóa sản phẩm khỏi giỏ hàng
    const handleDeleteItem = async (product_id) => {
        setCart((prevCart) => ({
            ...prevCart,
            items: prevCart.items.filter((item) => item.product !== product_id),
        }));

        try {
            await updateQuantityCart({ product_id, quantity: 0 });
            fetchCart();

        } catch (error) {
            toast.error("Lỗi khi xóa sản phẩm:", error);
            fetchCart();
        }
    };

    // Tính tổng tiền đơn hàng
    const totalOrderPrice = cartItems.reduce((total, item) => total + item.product_price * item.quantity, 0);

    // Tính tổng số lượng món
    const totalQuantity = cartItems.reduce((total, item) => total + item.quantity, 0);

    // Dat mon
    const handleOrderSubmit = async () => {
        try {
            const response = await createInvoice();
            const statusCode = response?.status || response?.headers?.status;

            if (statusCode === 201) {
                toast.success("Đặt món thành công!!", {
                    autoClose: 1000,
                    onClose: async () => {
                        // Đợi 1 tí cho chắc chắn toast biến mất (nếu cần)
                        await new Promise(resolve => setTimeout(resolve, 50));
                        await fetchCart();
                        await setCart({ items: [] });
                        navigate(`${config.routes.statusOrder}`);
                    },
                });
            }
        } catch (error) {
            toast.error(error.response?.data?.error || "Có lỗi xảy ra khi đặt hàng!");
        }
    };


    return (
        <div className={cx("container")}>
            <div className="row">
                <div className="col-12 text-center mt-3 text-white">
                    <button
                        onClick={() => navigate("/menu-order")}
                        className={cx("back-button")}
                    >
                        <FaArrowLeft />
                    </button>
                    <h2 className={cx("order-title", "fw-bold")}>{t("order_page.title")}</h2>
                </div>
            </div>

            {loading ? (
                <div className="text-center mt-4">
                    <PulseLoader color="#ffffff" />
                </div>
            ) : cartItems.length === 0 ? (
                <div className="text-center mt-4 text-white">
                    <h4>{t("order_page.empty_cart")}</h4>
                </div>
            ) : (
                cartItems.map((item, index) => (
                    <div className="row mt-3 w-100" key={item.id}>
                        <div className="col-12">
                            <div className={cx("order-item")}>
                                <span className={cx("index")}>{index + 1}</span>
                                <img
                                    src={item.product_image_url}
                                    alt={item.product_name}
                                    className={cx("food-image")}
                                />
                                <div className={cx("order-details")}>
                                    <h4 className={cx("food-name")}>{item.product_name}</h4>
                                    <div className={cx("quantity", "mt-3", "text-white")}>
                                        <span className={cx("price")}>{(item.product_price || 0).toLocaleString()}đ</span>
                                        <span className={cx("quantity-multiplier")}> x {item.quantity}</span>
                                    </div>
                                    <div className={cx("food-add-cart")}>
                                        <div className={cx("counter")}>
                                            <button
                                                className={cx("button")}
                                                onClick={() => handleDecreaseQuantity(item.product, item.quantity)}
                                                disabled={item.quantity <= 1} // Không giảm số lượng dưới 1
                                            >
                                                −
                                            </button>
                                            <span className={cx("count")}>{item?.quantity}</span>
                                            <button
                                                className={cx("button")}
                                                onClick={() => handleIncreaseQuantity(item.product, item.quantity)}
                                            >
                                                +
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                <span className={cx("total-price")}>
                                    {((item.product_price || 0) * (item.quantity || 0)).toLocaleString()} đ
                                </span>
                                <span className={cx("cs-deleted")} onClick={() => handleDeleteItem(item.product)}>
                                    <ImBin />
                                </span>
                            </div>
                        </div>
                    </div>
                ))
            )}

            {cartItems.length > 0 && (
                <>
                    <div className="row w-100">
                        <div className="col-12">
                            <div className={cx("order-summary")}>
                                <div className={cx("summary-content")}>
                                    <div className={cx("summary-row")}>
                                        <span className={cx("summary-label")}>{t("order_page.quantity")}</span>
                                        <span className={cx("summary-value")}>{totalQuantity} món</span>
                                    </div>
                                    <div className={cx("summary-row", "total-row")}>
                                        <span className={cx("summary-label", "total-label")}>{t("order_page.total")}</span>
                                        <span className={cx("summary-value", "total-value")}>{totalOrderPrice.toLocaleString()} đ</span>
                                    </div>
                                </div>
                                <div className={cx("order-action")}>
                                    <button
                                        type="button"
                                        className={cx("cs-btn-order")}
                                        onClick={handleOrderSubmit}
                                    >
                                        {t("order_page.button")}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default Order;