function displayNotification(message, level = "info") {
  toastr.options = {
    closeButton: true, // Cho phép người dùng tắt thông báo
    progressBar: true, // Thanh tiến trình thời gian
    newestOnTop: true, // Hiển thị thông báo mới lên đầu
    timeOut: 4000, // Thời gian hiển thị mặc định (ms)
    extendedTimeOut: 1000, // Khi người dùng hover
    positionClass: "toast-top-right", // Vị trí góc phải trên cùng
    preventDuplicates: true, // Tránh trùng lặp cùng message
    showEasing: "swing",
    hideEasing: "linear",
    showMethod: "fadeIn",
    hideMethod: "fadeOut",
  };
  const toastrMap = {
    success: () => toastr.success(message),
    error: () => toastr.error(message),
    warning: () => toastr.warning(message,),
    info: () => toastr.info(message),
    payment: () => toastr.info(message)
  };

  const notify = toastrMap[level] || toastrMap["info"];
  notify();
}

// Khi nhận được thông báo từ server
socket.onmessage = function (event) {
  const data = JSON.parse(event.data);
  const message = data.message;
  const level = data.level;
  displayNotification(message, level);
  load_notification_list();
};

function socket_update_order_status_detail(type, product_name ='',table_id, status='') {
  if (socket.readyState === WebSocket.OPEN) {
    // Socket đã mở, có thể gửi ngay
    socket.send(JSON.stringify({
        type:type,
        product_name: product_name,
        table_id: table_id,
        product_status: status,
    }));
  }
}
