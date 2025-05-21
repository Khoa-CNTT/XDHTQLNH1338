import React, { useEffect, useState } from 'react';
import { FaBell } from 'react-icons/fa';
import { IoClose } from "react-icons/io5";
import styles from './CallStaffButton.module.scss';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';

const CallStaffButton = () => {
  const [bottomPosition, setBottomPosition] = useState('4rem');
  const [showModal, setShowModal] = useState(false);
  const { t } = useTranslation();
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY + window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      
      if (documentHeight - scrollPosition < 100) {
        setBottomPosition('11rem');
      } else {
        setBottomPosition('4rem');
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleCallStaff = () => {
    setShowModal(true);
  };

  const handleConfirm = () => {
    // TODO: Implement staff calling logic
    console.log('Calling staff...');
    setShowModal(false);
  };

  const handleCancel = () => {
    setShowModal(false);
  };

  // Kiểm tra nếu đang ở trang order hoặc status-order thì không hiển thị chuông
  if (location.pathname.includes('/order') || location.pathname.includes('/status-order')) {
    return null;
  }

  return (
    <>
      <button 
        className={styles.bellButton} 
        onClick={handleCallStaff}
        style={{ bottom: bottomPosition }}
      >
        <FaBell className={styles.bellIcon} />
      </button>

      {showModal && (
        <div className={styles.modalOverlay} onClick={handleCancel}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <button className={styles.closeButton} onClick={handleCancel}>
              <IoClose />
            </button>
            <h2 className={styles.modalTitle}>{t('call_staff.title')}</h2>
            <p className={styles.modalMessage}>{t('call_staff.message')}</p>
            <div className={styles.buttonGroup}>
              <button className={styles.confirmButton} onClick={handleConfirm}>
                {t('call_staff.confirm')}
              </button>
              <button className={styles.cancelButton} onClick={handleCancel}>
                {t('call_staff.cancel')}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default CallStaffButton; 