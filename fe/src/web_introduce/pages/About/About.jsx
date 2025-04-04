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
              <h2>We Are Feane</h2>
            </div>
            <p className={cx('cs-text')}>{`There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don't look even slightly believable. If you are going to use a passage of Lorem Ipsum, you need to be sure there isn't anything embarrassing hidden in the middle of text. All`}</p>
            <button className={cx('cs-btn')}>Read more</button>
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