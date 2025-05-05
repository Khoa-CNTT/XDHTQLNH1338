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

// WebSocket setup
const socket = new WebSocket("ws://localhost:5001/ws/notifications/order/");

socket.onmessage = function (event) {
  console.log("Received:", event.data);
};

socket.onerror = function (err) {
  console.error("WebSocket error", err);
};

socket.onclose = function () {
  console.log("WebSocket closed");
};

// Khi nhận được thông báo từ server
socket.onmessage = function (event) {
  const data = JSON.parse(event.data);
  const message = data.message;
  const type = data.type;
  const level = data.level;

  if (type == "required_payment_cash") {
    console.log("type", type);
  }

  displayNotification(message, level);
  load_notification_list();
};
