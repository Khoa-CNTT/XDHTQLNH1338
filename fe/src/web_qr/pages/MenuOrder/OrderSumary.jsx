import React, { useEffect, useMemo, useRef, useState } from "react";
import styles from "./Menu.module.scss";
import classNames from "classnames/bind";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { useCart } from "../../context/CartContext";

const cx = classNames.bind(styles);

export default function OrderSummary({ isFooterVisible }) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { cart } = useCart();
    const cartItems = cart?.items || [];

    // useRef lưu giá trị trước đó để tránh re-render liên tục
    const prevTotalPriceRef = useRef(0);
    const prevTotalItemsRef = useRef(0);

    // State giữ giá trị để cập nhật UI mượt hơn
    const [displayPrice, setDisplayPrice] = useState(0);
    const [displayItems, setDisplayItems] = useState(0);

    // Tính tổng số lượng món ăn
    const totalItems = useMemo(() =>
        cartItems.reduce((sum, item) => sum + item.quantity, 0),
        [cartItems]);

    // Tính tổng giá tiền
    const totalPrice = useMemo(() =>
        cartItems.reduce((sum, item) => sum + item.quantity * item.product_price, 0),
        [cartItems]);

    // Cập nhật UI mượt hơn khi giá trị thay đổi
    useEffect(() => {
        if (totalPrice !== prevTotalPriceRef.current) {
            setTimeout(() => setDisplayPrice(totalPrice), 200); // Thêm delay nhỏ để tránh chớp
            prevTotalPriceRef.current = totalPrice;
        }
    }, [totalPrice]);

    useEffect(() => {
        if (totalItems !== prevTotalItemsRef.current) {
            setTimeout(() => setDisplayItems(totalItems), 200);
            prevTotalItemsRef.current = totalItems;
        }
    }, [totalItems]);

    const formatCurrency = (price) =>
        new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(price);

    const handleClick = () => {
        if (totalItems > 0) {
            navigate("/order");
        }
    };

    return (
        <div className={cx("order-summary", { "move-up": isFooterVisible, disabled: totalItems === 0 })}>
            <span className={cx("text")} onClick={handleClick}>
                {t("order_summary.title")} · {t("order_summary.items", { count: displayItems })}
            </span>
            <span className={cx("price")}>{formatCurrency(displayPrice)}</span>
        </div>
    );
}