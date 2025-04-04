import { useContext } from 'react'
import config from '../../config'
import './BuyTimeComplete.css'
import { ThemeContext } from '../../layout/DefaultLayout/DefaultLayout'

const BuyTimeComplete = () => {
  const { totalPay } = useContext(ThemeContext)
  const formatNumber = (number) => {
    return number.toLocaleString('vi-VN')
  }

  return <div className='container d-flex align-item-center justify-content-center '>
    <div className="cs-card-pay cs-border-none card mt-5">
      <div className="cs-content-card">
        <span className='cs-text-success'>Yêu cầu nạp tiền thành công</span>
        <div className="cs-check-icon mt-4"></div>
        <span className='cs-text-desc mt-4'>Đơn hàng của quý khách đang được xử lý</span>
        <span className='text-center cs-text-success mt-3'>{totalPay && formatNumber(totalPay)} vnđ</span>
      </div>
      <div className="row mt-5">
        <div className="col-6">
          <a href={`${config.routes.depositHistory}`} className="btn cs-btn">Xem trạng trạng thái yêu cầu</a>
        </div>
        <div className="col-6">
          <a href={`${config.routes.buyTime}`} className="btn cs-btn">Mua thêm giờ</a>
        </div>
      </div>
    </div>
  </div>
}

export default BuyTimeComplete