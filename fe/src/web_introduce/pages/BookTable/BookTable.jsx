import classNames from 'classnames/bind';
import styles from './BookTable.module.scss';
import { TbBrandAirtable } from "react-icons/tb";
import { useEffect, useState } from 'react';
import { readTable } from '../../services/api';

const cx = classNames.bind(styles);

const BookTable = () => {
  const [listTable, setListTable] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null); // Lưu bàn đang chọn
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    persons: '',
    time: '00:00',
    date: ''
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const tables = await readTable();
        setListTable(tables?.data || []);
      } catch (error) {
        console.error("Error fetching table data:", error);
      }
    };
    fetchData();
  }, []);

  const handleSelectTable = (table) => {
    if (table.status === "available") {
      setSelectedTable(table.table_number); // Lưu bàn đang chọn
    }
  };
  const handleSubmit = (e) => {
    e.preventDefault();

    const bookingInfo = {
      ...formData,
      table: selectedTable
    };
    console.log('Booking Information:', bookingInfo);
  };

  return (
    <div className={cx('wrapper')}>
      <div className={cx('container')}>
        <div className={cx('cx-body')}>
          <div className='row'>
            {/* <div className='col-md-6 d-flex justify-content-center'>
              <div className={cx('cs-table', 'd-flex flex-wrap justify-content-between')}>
                {listTable.map((item, index) => {
                  const isSelected = selectedTable === item.table_number;
                  const tableClass = cx(
                    'cs-table-item',
                    'col-2 me-4 mb-4',
                    isSelected ? 'bg-success' : item.status === "occupied" ? 'bg-danger' : 'bg-light'
                  );

                  return (
                    <div
                      key={index}
                      className={tableClass}
                      onClick={() => handleSelectTable(item)}
                      style={{
                        cursor: item.status === "occupied" ? 'not-allowed' : 'pointer',
                        opacity: item.status === "occupied" ? 0.6 : 1,
                        color: item.status === "occupied" ? '#fff' : '#000',
                      }}
                    >
                      <div className={cx('cs-table-icon')}><TbBrandAirtable /></div>
                      <div className={cx('cs-table-name')}>Table {item?.table_number}</div>
                    </div>
                  );
                })}
              </div>
            </div> */}
            <div className='col-md-6'>
              <div className={cx('cs-header')}>Book A Table</div>
              <div className={cx('cs-form-info')}>
                <form>
                  <div className="form-floating">
                    <input type="text" className={cx('form-control', 'cs-form-item')} id="floatingInputName" placeholder='' required />
                    <label htmlFor="floatingInputName">Your name?</label>
                  </div>
                  <div className="form-floating">
                    <input type="text" className={cx('form-control', 'cs-form-item')} id="floatingInputPhone" placeholder='' required />
                    <label htmlFor="floatingInputPhone">Your phone number?</label>
                  </div>
                  <div className="form-floating">
                    <input type="text" className={cx('form-control', 'cs-form-item')} id="floatingInputNumber" placeholder='' />
                    <label htmlFor="floatingInputNumber">How many persons?</label>
                  </div>
                  <div className="form-floating">
                    <input
                      type="text"
                      className={cx('form-control', 'cs-form-item')}
                      id="floatingInputTable"
                      placeholder=''
                      value={selectedTable || ""}
                      readOnly
                    />
                    <label htmlFor="floatingInputTable">Which table do you choose?</label>
                  </div>
                  <div className="form-floating">
                    <input type="time" className={cx('form-control', 'cs-form-item')} id="floatingInputTime" placeholder='' defaultValue='00:00' />
                    <label htmlFor="floatingInputTime">What time do you book a table?</label>
                  </div>
                  <div className="form-floating">
                    <input type="date" className={cx('form-control', 'cs-form-item')} id="floatingInputValue" placeholder='' />
                    <label htmlFor="floatingInputValue">What day do you book a table?</label>
                  </div>
                  <button type='submit' className={cx('cs-form-btn')}>BOOK NOW</button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookTable;
