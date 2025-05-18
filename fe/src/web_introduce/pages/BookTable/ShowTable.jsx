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
{/* <div className="form-floating">
                    <input
                      type="text"
                      className={cx('form-control', 'cs-form-item')}
                      id="floatingInputTable"
                      placeholder=''
                      value={selectedTable || ""}
                      readOnly
                    />
                    <label htmlFor="floatingInputTable">Which table do you choose?</label>
                  </div> */}
// .cs-table-item {
//     display: flex;
//     flex-direction: column;
//     justify-content: center;
//     align-items: center;
//     border: 1px solid;
//     border-radius: 15px;
//     box-shadow: 1px 1px 1px 1px rgba(0.2, 0.2, 0.2, .2) !important;;

//     &:hover {
//         cursor: pointer;
//     }
//     .cs-table-icon {
//         font-size: 35px;
//     }
//     .cs-table-name{
//         font-weight: 400;
//         font-size: 17px;
//     }
// }