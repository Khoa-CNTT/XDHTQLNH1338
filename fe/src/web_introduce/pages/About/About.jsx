import classNames from 'classnames/bind'
import styles from './About.module.scss'

const cx = classNames.bind(styles)

const About = () => {
  return (
    <div className={cx('wrapper')}>
      <div className={cx('container')}>
        <div className={cx('row d-flex align-items-center justify-content-center')}>
          <div className={cx('col-12 col-md-6 order-md-2', 'cs-content')}>
            <div className={cx('cs-header')}>
              <h2>We Are Five Star</h2>
            </div>
            <p className={cx('cs-text')}>{`Nhà hàng ẩm thực hiện đại kết hợp với truyền thống, tạo nên tính mới lạ cho thực khách. Được ra đời vào năm 2025 với tiêu chí "Khách hàng là trên hết, phục vụ nhanh chóng" nên chúng tôi luôn tự hào về cách phục vụ cũng như các món ăn mà chúng tôi làm ra. Nhà hàng chúng tôi luôn luôn đặt khách hàng lên hàng đầu, tận tâm phục vụ, mang lại cho khách hàng những trãi nghiệm tuyệt với nhất. Các món ăn với công thức độc quyền sẽ mang lại hương vị mới mẻ cho thực khách. Chúng tôi xin chân thành cảm ơn.`}</p>
            <button className={cx('cs-btn')}>Xem thêm</button>
          </div>
          <div className={cx('col-12 col-md-6 order-md-1', 'cs-img')}>
            <div className={cx('cs-img-box')}><img src="https://themewagon.github.io/feane/images/about-img.png" alt="" /></div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default About