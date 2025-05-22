import classNames from 'classnames/bind'
import styles from './Header.module.scss'

import { Link } from "react-router-dom";
import { IoSearch } from "react-icons/io5";
import { FaUser, FaBars, FaTimes } from "react-icons/fa";
import config from "../../../config";
import { createContext, useState, useRef, useEffect } from 'react';
import Search from './Search/Search';

const cx = classNames.bind(styles)


export const ToggleSearchFullscreenContext = createContext(null);
const Header = () => {
  const [blockSearchFullscreen, setBlockSearchFullscreen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const mobileMenuRef = useRef(null);

  const handleSearchFullscreen = (e) => {
    e.preventDefault();
    setBlockSearchFullscreen((pre) => !pre);
  };

  const handleClose = () => {
    setBlockSearchFullscreen((pre) => !pre);
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(prev => !prev);
  };

  // Close mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (mobileMenuRef.current && !mobileMenuRef.current.contains(event.target) && 
          !event.target.classList.contains(cx('cs-mobile-menu-icon'))) {
        setMobileMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <header className={cx('cs-bg-header')}>
      <div className={cx('container h-100 d-flex justify-content-between align-items-center')}>
        <Link to={config.routes.home} className={cx('cs-logo')}>RYAN PHAM</Link>
        
        {/* Desktop Menu */}
        <div className={cx('cs-desktop-menu', 'd-flex justify-content-between', 'd-none d-md-flex')}>
          <Link to={config.routes.home} className={cx('cs-text-center')}>HOME</Link>
          <Link to={config.routes.menu} className={cx('cs-text-center')}>MENU</Link>
          <Link to={config.routes.about} className={cx('cs-text-center')}>ABOUT</Link>
          <Link to={config.routes.bookTable} className={cx('cs-text-center')}>FEEDBACK</Link>
        </div>
        
        <div className={cx('', 'cs-nav-right')}>
          <IoSearch className={cx('cs-icon')} onClick={handleSearchFullscreen} />
          <Link to={config.routes.bookTable} className={cx('cs-btn-primary')}>Book a table</Link>
          <FaBars className={cx('cs-mobile-menu-icon')} onClick={toggleMobileMenu} />
        </div>
      </div>
      
      {/* Mobile Menu */}
      <div ref={mobileMenuRef} className={cx('cs-mobile-menu', { 'cs-mobile-menu-open': mobileMenuOpen })}>
        <div className={cx('cs-mobile-menu-header')}>
          <Link to={config.routes.home} className={cx('cs-logo')}>RYAN PHAM</Link>
          <FaTimes className={cx('cs-icon')} onClick={toggleMobileMenu} />
        </div>
        <div className={cx('cs-mobile-menu-links')}>
          <Link to={config.routes.home} className={cx('cs-mobile-text-center')} onClick={toggleMobileMenu}>HOME</Link>
          <Link to={config.routes.menu} className={cx('cs-mobile-text-center')} onClick={toggleMobileMenu}>MENU</Link>
          <Link to={config.routes.about} className={cx('cs-mobile-text-center')} onClick={toggleMobileMenu}>ABOUT</Link>
          <Link to={config.routes.bookTable} className={cx('cs-mobile-text-center')} onClick={toggleMobileMenu}>FEEDBACK</Link>
          <Link to={config.routes.bookTable} className={cx('cs-mobile-btn-primary')} onClick={toggleMobileMenu}>Book a table</Link>
        </div>
      </div>
      
      <div className={cx('cs-logo-large')}><img className={cx('cs-img-large')} src='https://res.cloudinary.com/daehcveku/image/upload/v1741257938/upload_local/ihd7hrj43mlqt4xoetlh.jpg' /></div>
      {/* search fullscreen */}
      <ToggleSearchFullscreenContext.Provider value={handleClose}>
        <Search
          blockSearchFullscreen={blockSearchFullscreen}
          handleClose={handleClose}
        />
      </ToggleSearchFullscreenContext.Provider>
    </header>
  )
}


export default Header

