import classNames from 'classnames/bind'
import styles from './BookTable.module.scss'
import { TbBrandAirtable } from "react-icons/tb"
import { useEffect, useState } from 'react'
import { readTable } from '../../services/api'

const cx = classNames.bind(styles);

const BookTable = () => {
  const [listTable, setListTable] = useState([])
  const [selectedTable, setSelectedTable] = useState(null) // Lưu bàn đang chọn

  useEffect(() => {
    const fetchData = async () => {
      try {
        const tables = await readTable()
        setListTable(tables?.data || [])
      } catch (error) {
        console.error("Error fetching table data:", error)
      }
    }
    fetchData()
  }, [])

  const handleSelectTable = (table) => {
    if (table.status === "available") {
      setSelectedTable(table.table_number) // Lưu bàn đang chọn
    }
  };

  return (
    <div className={cx('wrapper')}>
      <div className={cx('container')}>
        <div className={cx('cx-body')}>
          <div className='d-flex justify-content-center'>
            <div className="col-md-8">
              <div className={cx('booking-form')}>
                <h2 className={cx('form-title', 'text-center mb-4')}>Liên hệ đặt bàn</h2>
                <form className='d-flex flex-wrap justify-content-around'>
                  {/* Name Field */}
                  <div className="mb-3 col-md-5 col-12">
                    <label htmlFor="name" className="form-label">Tên của bạn:</label>
                    <input
                      type="text"
                      className={`form-control ${cx('form-input')}`}
                      id="name"
                      placeholder="Tên của bạn..."
                      required
                    />
                  </div>
                  {/* Phone Field */}
                  <div className="mb-3 col-md-5 col-12">
                    <label htmlFor="phone" className="form-label">Số điện thoại của bạn:</label>
                    <input
                      type="tel"
                      className={`form-control ${cx('form-input')}`}
                      id="phone"
                      placeholder="Số điện thoại..."
                      required
                    />
                  </div>
                  {/* Number of People */}
                  <div className="mb-3 col-md-5 col-12">
                    <label htmlFor="guests" className="form-label">Bạn đi mấy người?</label>
                    <input
                      type="number"
                      className={`form-control ${cx('form-input')}`}
                      id="guests"
                      placeholder="Số người..."
                      min="1"
                    />
                  </div>
                  {/* Email Field */}
                  <div className="mb-3 col-md-5 col-12">
                    <label htmlFor="email" className="form-label">Email của bạn:</label>
                    <input
                      type="email"
                      className={`form-control ${cx('form-input')}`}
                      id="email"
                      placeholder="Email"
                    />
                  </div>
                  {/* Date and Time Row */}
                  <div className="col-md-5 mb-3 mb-md-0 col-12">
                    <label htmlFor="date" className="form-label">Bạn có thể đến ngày nào?</label>
                    <input
                      type="date"
                      className={`form-control ${cx('form-input')}`}
                      id="date"
                      placeholder="Chọn Ngày"
                    />
                  </div>
                  <div className="col-md-5 col-12">
                    <label htmlFor="time" className="form-label">Thời gian bạn đến?</label>
                    <input
                      type="time"
                      className={`form-control ${cx('form-input')}`}
                      id="time"
                      placeholder="..."
                    />
                  </div>
                  {/* Submit Button */}
                  <button type="submit" className={`col-md-5 d-flex justify-content-center ${cx('submit-btn')}`}>
                    Đặt bàn ngay
                  </button>
                </form>
                {/* Footer Note */}
                <p className={cx('note-text', 'text-center mt-3 mb-0')}>
                  Khách đặt tiệc hội nghị, liên hoan vui lòng gọi trực tiếp: <strong>1900 6750</strong>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default BookTable
