import React, { useState, useEffect } from "react";
import classNames from "classnames/bind";
import styles from "./Menu.module.scss";
import { readProduct, readCategory } from "../../services/api";
import { FaRegEye } from "react-icons/fa";

const cx = classNames.bind(styles);

const Menu = () => {
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);

  const fetchCategories = async () => {
    try {
      const response = await readCategory();
      setCategories(response?.data || []);
    } catch (error) {
      console.error("Error fetching category data:", error);
    }
  };

  const fetchData = async (categoryId = null) => {
    try {
      const response = await readProduct({ category_id: categoryId });
      setProducts(response?.data?.results || []);
    } catch (error) {
      console.error("Error fetching product data:", error);
    }
  };

  useEffect(() => {
    fetchCategories();
    fetchData();
  }, []);

  const handleCategoryChange = (categoryId) => {
    setSelectedCategory(categoryId);
    fetchData(categoryId === "All" ? null : categoryId);
  };

  return (
    <div className={cx("menu-container")}>
      <h2 className={cx("menu-title")}>Our Menu</h2>

      {/* Danh mục filter */}
      <div className={cx("category-filter")}>
        <button
          className={cx("filter-button", { active: selectedCategory === "All" })}
          onClick={() => handleCategoryChange("All")}
        >
          Tất cả
        </button>
        {categories.map(category => (
          <button
            key={category.id}
            className={cx("filter-button", { active: selectedCategory === category.id })}
            onClick={() => handleCategoryChange(category.id)}
          >
            {category.name}
          </button>
        ))}
      </div>

      <div className={cx("menu-items")}>
        {products.length > 0 ? (
          products.map(item => (
            <div key={item.id} className={cx("menu-card")}>
              <div className={cx("menu-image-wrapper")}>
                <img src={item?.image_url} alt={item.name} className={cx("menu-image")} />
              </div>
              <div className={cx("menu-info")}>
                <h3 className={cx("menu-name")}>{item.name}</h3>
                <p className={cx("menu-description")}>{item.description}</p>
                <div className={cx("menu-footer")}>
                  <span className={cx("menu-price")}>{item.price.toLocaleString()} VNĐ</span>
                  <button className={cx("cart-button")}>
                    <FaRegEye />
                  </button>
                </div>
              </div>
            </div>
          ))
        ) : (
          <p className={cx("no-product")}>Không có sản phẩm nào trong danh mục này.</p>
        )}
      </div>

      <button className={cx("view-more-button")}>View More</button>
    </div>
  );
};

export default Menu;
