import classNames from 'classnames/bind'
import styles from './BookTable.module.scss'
import { useState, useEffect } from 'react'
import { toast } from 'react-toastify'
import axios from 'axios'
const cx = classNames.bind(styles)

const BookTable = () => {
  const [formData, setFormData] = useState({
    name: '',
    phone_number: '',
    many_person: '',
    // table: '',
    date: '',
    hour: '00:00'
  })
  const [isLoading, setIsLoading] = useState(false)
  const [minDate, setMinDate] = useState('')

  useEffect(() => {
    // Set the minimum date to today's date
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    setMinDate(`${year}-${month}-${day}`)
  }, [])

  const handleChange = (e) => {
    const { id, value } = e.target
    setFormData((prev) => ({ ...prev, [id]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)

    const { name, phone_number, many_person, date, hour } = formData

    // Validation checks
    if (!name || !phone_number || !many_person || !date || !hour) {
      toast.error('Vui lòng điền đầy đủ thông tin!')
      setIsLoading(false)
      return
    }

    const phoneRegex = /^0\d{9}$/
    if (!phoneRegex.test(phone_number)) {
      toast.error('Số điện thoại không hợp lệ! (10 chữ số, bắt đầu bằng 0)')
      setIsLoading(false)
      return
    }

    const personNum = parseInt(many_person)
    if (isNaN(personNum) || personNum < 1) {
      toast.error('Số người phải là số nguyên >= 1!')
      setIsLoading(false)
      return
    }

    const selectedDate = new Date(date)
    if (selectedDate < minDate) {
      toast.error('Ngày đến không được ở quá khứ!')
      setIsLoading(false)
      return
    }

    try {
      const response = await axios.post('http://localhost:8000/api/book/tables/reservations/', formData)
      toast.success(response.data.message)
      setFormData({
        name: '',
        phone_number: '',
        many_person: '',
        // table: '',
        date: '',
        hour: '00:00'
      })
    } catch (error) {
      toast.error(error.response.data.message || 'Có lỗi xảy ra, vui lòng thử lại!')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={cx('wrapper')}>
      <div className={cx('container')}>
        <div className={cx('cs-body')}>
          <div className='d-flex justify-content-center'>
            <div className='col-md-6'>
              <div className={cx('cs-booking-form')}>
                <h2 className={cx('cs-form-title', 'text-center mb-4')}>Liên hệ đặt bàn</h2>
                <form className='d-flex flex-column align-items-center' onSubmit={handleSubmit}>
                  {/* Name Input */}
                  <div className='mb-3 col-md-10 col-12'>
                    <label htmlFor='name' className={cx('cs-form-label')}>Tên của bạn:</label>
                    <input
                      type='text'
                      className={`form-control ${cx('cs-form-input')}`}
                      id='name'
                      value={formData.name}
                      onChange={handleChange}
                      placeholder='Tên của bạn...'
                    />
                  </div>
                  {/* Phone Input */}
                  <div className='mb-3 col-md-10 col-12'>
                    <label htmlFor='phone_number' className={cx('cs-form-label')}>Số điện thoại của bạn:</label>
                    <input
                      type='tel'
                      className={`form-control ${cx('cs-form-input')}`}
                      id='phone_number'
                      value={formData.phone_number}
                      onChange={handleChange}
                      placeholder='Số điện thoại...'
                    />
                  </div>
                  {/* Persons Input */}
                  <div className='mb-3 col-md-10 col-12'>
                    <label htmlFor='many_person' className={cx('cs-form-label')}>Bạn đi mấy người?</label>
                    <input
                      type='number'
                      className={`form-control ${cx('cs-form-input')}`}
                      id='many_person'
                      value={formData.many_person}
                      onChange={handleChange}
                      placeholder='Số người...'
                      min='1'
                    />
                  </div>
                  {/* Date Input */}
                  <div className='mb-3 col-md-10 col-12'>
                    <label htmlFor='date' className={cx('cs-form-label')}>Bạn có thể đến ngày nào?</label>
                    <input
                      type='date'
                      className={`form-control ${cx('cs-form-input')}`}
                      id='date'
                      value={formData.date}
                      onChange={handleChange}
                      min={minDate}
                    />
                  </div>
                  {/* Time Input */}
                  <div className= 'col-md-10 col-12'>
                    <label htmlFor='hour' className={cx('cs-form-label')}>Thời gian bạn đến?</label>
                    <input
                      type='time'
                      className={`form-control ${cx('cs-form-input')}`}
                      id='hour'
                      value={formData.hour}
                      onChange={handleChange}
                    />
                  </div>
                  {/* Submit Button */}
                  <button
                    type='submit'
                    className={`col-md-6 col-8 d-flex justify-content-center mt-3 ${cx('cs-submit-btn')}`}
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <div className="spinner-border text-light" role="status">
                        <span className="visually-hidden">Loading...</span>
                      </div>
                    ) : (
                      'Đặt bàn ngay'
                    )}
                  </button>
                </form>

                {/* Footer Note */}
                <p className={cx('cs-note-text', 'text-center mt-3 mb-0')}>
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
