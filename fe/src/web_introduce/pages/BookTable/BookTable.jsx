import classNames from 'classnames/bind'
import styles from './BookTable.module.scss'
import { useState } from 'react'
import { toast } from 'react-toastify';

const cx = classNames.bind(styles)

const BookTable = () => {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    persons: '',
    time: '00:00',
    date: ''
  })

  const handleChange = (e) => {
    const { id, value } = e.target
    setFormData((prev) => ({ ...prev, [id]: value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    const { name, phone, persons, time, date, email } = formData

    if (!name || !phone || !persons || !time || !date || !email) {
      toast.error('Vui lòng điền đầy đủ thông tin!')
      return
    }

    const phoneRegex = /^0\d{9}$/
    if (!phoneRegex.test(phone)) {
      toast.error('Số điện thoại không hợp lệ! (10 chữ số, bắt đầu bằng 0)')
      return
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      toast.error('Email không hợp lệ!')
      return
    }

    const personNum = parseInt(persons)
    if (isNaN(personNum) || personNum < 1) {
      toast.error('Số người phải là số nguyên >= 1!')
      return
    }

    const selectedDate = new Date(date)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    if (selectedDate < today) {
      toast.error('Ngày đến không được ở quá khứ!')
      return
    }

    console.log('Thông tin đặt bàn:', formData)
    toast.success('Đặt bàn thành công!')
  }

  return (
    <div className={cx('wrapper')}>
      <div className={cx('container')}>
        <div className={cx('cs-body')}>
          <div className='d-flex justify-content-center'>
            <div className='col-md-8'>
              <div className={cx('cs-booking-form')}>
                <h2 className={cx('cs-form-title', 'text-center mb-4')}>Liên hệ đặt bàn</h2>
                <form className='d-flex flex-wrap justify-content-around' onSubmit={handleSubmit}>
                  {/* Name */}
                  <div className='mb-3 col-md-5 col-12'>
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

                  {/* Phone */}
                  <div className='mb-3 col-md-5 col-12'>
                    <label htmlFor='phone' className={cx('cs-form-label')}>Số điện thoại của bạn:</label>
                    <input
                      type='tel'
                      className={`form-control ${cx('cs-form-input')}`}
                      id='phone'
                      value={formData.phone}
                      onChange={handleChange}
                      placeholder='Số điện thoại...'
                    />
                  </div>

                  {/* Persons */}
                  <div className='mb-3 col-md-5 col-12'>
                    <label htmlFor='persons' className={cx('cs-form-label')}>Bạn đi mấy người?</label>
                    <input
                      type='number'
                      className={`form-control ${cx('cs-form-input')}`}
                      id='persons'
                      value={formData.persons}
                      onChange={handleChange}
                      placeholder='Số người...'
                      min='1'
                    />
                  </div>

                  {/* Email */}
                  <div className='mb-3 col-md-5 col-12'>
                    <label htmlFor='email' className={cx('cs-form-label')}>Email của bạn:</label>
                    <input
                      type='email'
                      className={`form-control ${cx('cs-form-input')}`}
                      id='email'
                      value={formData.email}
                      onChange={handleChange}
                      placeholder='Email'
                    />
                  </div>

                  {/* Date */}
                  <div className='col-md-5 mb-3 mb-md-0 col-12'>
                    <label htmlFor='date' className={cx('cs-form-label')}>Bạn có thể đến ngày nào?</label>
                    <input
                      type='date'
                      className={`form-control ${cx('cs-form-input')}`}
                      id='date'
                      value={formData.date}
                      onChange={handleChange}
                      
                    />
                  </div>

                  {/* Time */}
                  <div className='col-md-5 col-12'>
                    <label htmlFor='time' className={cx('cs-form-label')}>Thời gian bạn đến?</label>
                    <input
                      type='time'
                      className={`form-control ${cx('cs-form-input')}`}
                      id='time'
                      value={formData.time}
                      onChange={handleChange}
                      
                    />
                  </div>

                  {/* Submit */}
                  <button
                    type='submit'
                    className={`col-md-5 d-flex justify-content-center mt-3 ${cx('cs-submit-btn')}`}
                  >
                    Đặt bàn ngay
                  </button>
                </form>

                {/* Footer */}
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
