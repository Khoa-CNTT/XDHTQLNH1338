import classNames from 'classnames/bind'
import styles from './Header.module.scss'

import { Link } from "react-router-dom";
import { IoSearch } from "react-icons/io5";
import { FaUser } from "react-icons/fa";
import config from "../../../config";
import { createContext, useState } from 'react';
import Search from './Search/Search';

const cx = classNames.bind(styles)


export const ToggleSearchFullscreenContext = createContext(null);
const Header = () => {
  const [blockSearchFullscreen, setBlockSearchFullscreen] = useState(false);

  const handleSearchFullscreen = (e) => {
    e.preventDefault();
    setBlockSearchFullscreen((pre) => !pre);
  };

  const handleClose = () => {
    setBlockSearchFullscreen((pre) => !pre);
  };
  return (
    <header className={cx('cs-bg-header')}>
      <div className={cx('container h-100 d-flex justify-content-between align-items-center')}>
        <Link to={config.routes.home} className={cx('cs-logo')}>RYAN PHAM</Link>
        <div className={cx('d-flex justify-content-between')}>
          <Link to={config.routes.home} className={cx('cs-text-center')}>HOME</Link>
          <Link to={config.routes.menu} className={cx('cs-text-center')}>MENU</Link>
          <Link to={config.routes.about} className={cx('cs-text-center')}>ABOUT</Link>
          <Link to={config.routes.bookTable} className={cx('cs-text-center')}>FEEDBACK</Link>
        </div>
        <div className={cx('d-flex justify-content-end')}>
          {/* <FaUser className={cx('cs-icon')} /> */}
          <IoSearch className={cx('cs-icon')} onClick={handleSearchFullscreen} />
          <Link to={config.routes.bookTable} className={cx('cs-btn-primary')}>Book a table</Link>
          <div className={cx('d-flex align-items-center')}>
            <select className={cx('cs-select-language')} aria-label="Default select example">
              <option value="1">Vietnamese</option>
              <option value="2">English</option>
            </select>
          </div>
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

