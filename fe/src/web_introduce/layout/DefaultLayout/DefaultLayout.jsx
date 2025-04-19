import { createContext, useState } from "react"
export const ThemeContext = createContext(null)
import classNames from "classnames/bind"
import styles from "./DefaultLayout.module.scss"


import Header from "./components/Header"
import Footer from "./components/Footer"
import { useParams } from "react-router-dom"

const cx = classNames.bind(styles)

const DefaultLayout = ({ children }) => {
  const [totalPay, setTotalPay] = useState(0)
  const { lang } = useParams()
  return (
    // <SocketProvider>
      <ThemeContext.Provider value={{ totalPay, setTotalPay, }}>
        <Header lang={lang} />
        <div className={cx('cs-container')}>{children}</div>
        <Footer />
      </ThemeContext.Provider>
    // </SocketProvider>
  )
}

export default DefaultLayout
