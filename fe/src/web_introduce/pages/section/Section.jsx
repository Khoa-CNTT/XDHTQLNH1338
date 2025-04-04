import { useState, useEffect } from 'react';
import classNames from 'classnames/bind';
import styles from './Section.module.scss';

const cx = classNames.bind(styles);

const slides = [
  {
    id: 1,
    title: "Fast Food Restaurant",
    text: "Doloremque, itaque aperiam facilis rerum, commodi, temporibus sapiente ad mollitia laborum quam quisquam esse error unde. Tempora ex doloremque, labore, sunt repellat dolore, iste magni quos nihil ducimus libero ipsam.",
    image: "https://themewagon.github.io/feane/images/f1.png"
  },
  {
    id: 2,
    title: "Delicious Burgers",
    text: "Experience the best and juiciest burgers with the freshest ingredients. Made with love and care to give you the best taste ever!",
    image: "https://themewagon.github.io/feane/images/f1.png"
  },
  {
    id: 3,
    title: "Tasty Fries & Drinks",
    text: "Enjoy crispy fries and refreshing beverages that perfectly complement your meal. A treat for your taste buds!",
    image: "https://themewagon.github.io/feane/images/f1.png"
  }
];

const Section = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prevSlide) => (prevSlide + 1) % slides.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className={cx("hero-section")}> 
      <div className={cx('hero-wrapper')}>
        <div className={cx('hero-container')}>
          <div className={cx('hero-content')}>
            <h1 className={cx('hero-title')}>{slides[currentSlide].title}</h1>
            <p className={cx('hero-text')}>{slides[currentSlide].text}</p>
            <button className={cx('hero-btn')}>Order Now</button>
          </div>
          <div className={cx('hero-image')}>
            <img src={slides[currentSlide].image} alt="Fast Food" className={cx('fade-in')} />
          </div>
        </div>
        {/* Pagination Dots */}
        <div className={cx('hero-dots')}>
          {slides.map((_, index) => (
            <span 
              key={index} 
              className={cx('dot', { active: index === currentSlide })}
              onClick={() => setCurrentSlide(index)}
            ></span>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Section;