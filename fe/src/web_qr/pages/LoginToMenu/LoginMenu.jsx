import classNames from 'classnames/bind';
import styles from './LoginMenu.module.scss';
import { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import { ClipLoader } from "react-spinners";
import { useAuth } from '../../context/AuthContext'
import { toast } from 'react-toastify';

const cx = classNames.bind(styles);

const LoginPage = () => {
    const { login, user } = useAuth()
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [tableNumber, setTableNumber] = useState(null);
    const [formData, setFormData] = useState({
        phoneNumber: "",
        username: "",
        lastName: "",
        firstName: "",
    });

    useEffect(() => {
        if (user) { navigate('/menu-order/vn'); }
    }, [user, navigate]);

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        setTableNumber(params.get('table_number'));
    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        if (!formData.phoneNumber.trim()) {
            toast.error("Số điện thoại không được để trống!");
            setLoading(false);
            return;
        }
        if (!/^\d{10}$/.test(formData.phoneNumber)) {
            toast.error("Số điện thoại phải có 10 chữ số!");
            setLoading(false);
            return;
        }
    
        if (!formData.firstName.trim()) {
            toast.error("Tên không được để trống!");
            setLoading(false);
            return;
        }

        setTimeout(async () => {
            try {
                let data = {
                    table_number: tableNumber,
                    phone_number: formData.phoneNumber,
                    username: formData.phoneNumber,
                    last_name: formData.firstName,
                    first_name: formData.firstName,
                };
                let res = await login(data);
                if (res && res.status === 200) {
                    navigate('/menu-order');
                } else {
                    toast.error(res?.response?.data?.error);
                }
            } catch (err) {
                toast.error(res?.response?.data?.error);
            } finally {
                setLoading(false);
            }
        }, 1000);
    };

    return (
        <div className={cx("login-container")}>
            <div className="row">
                <div className="col-12">
                    <div className={cx("login-box")}>
                        <h2 className={cx("welcome-text")}>Welcome</h2>
                        <div className={cx("form-container")}>
                            <h3 className={cx("sign-in-text")}>Đăng nhập gọi món</h3>
                            <form onSubmit={handleSubmit}>
                                <input type="text" name="phoneNumber" placeholder="Số điện thoại"
                                    value={formData.phoneNumber} onChange={handleChange} />

                                <input hidden type="text" name="username" placeholder="Tên đăng nhập"
                                    value={formData.phoneNumber} onChange={handleChange} />

                                <input type="text" name="firstName" placeholder="Tên"
                                    value={formData.firstName} onChange={handleChange} />

                                <button type="submit" className={cx("arrow-button")} disabled={loading}>
                                    {loading ? <ClipLoader size={25} /> : "→"}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;