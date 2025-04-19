function displayNotification(message) {
  toastr.options = {
    closeButton: true,
    progressBar: true,
    timeOut: 5000,
    extendedTimeOut: 1000,
    positionClass: "toast-top-right",
  };
  toastr.info(message, "Thông báo");
}

// WebSocket setup
const socket = new WebSocket("ws://0.0.0.0:5001/ws/notifications/order/");

// Khi nhận được thông báo từ server
socket.onmessage = function (event) {
  console.log("event", event);
  const data = JSON.parse(event.data);
  const message = data.message;
  console.log("message", message);
  displayNotification(message);
  load_notification_list();
};
