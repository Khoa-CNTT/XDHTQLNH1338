# XDHTQLNH1338 - Web Application

[English](#english) | [Tiếng Việt](#tiếng-việt)

## English

### Overview

This is a full-stack web application built with React (Frontend) and Django (Backend). The application features real-time capabilities, authentication, and various integrations.

### Tech Stack

#### Frontend

- React 18
- Vite
- Material-UI & Bootstrap
- React Query
- i18next (Internationalization)
- Styled Components & SASS
- Various utilities (PDF generation, QR codes, etc.)

#### Backend

- Django 5.1.3
- Django REST Framework
- Django Channels (WebSocket)
- Redis
- JWT Authentication
- Cloud Storage (Cloudinary)
- Docker support

### Prerequisites

- Node.js (v16 or higher)
- Python 3.8 or higher
- Docker and Docker Compose
- Redis

### Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd XDHTQLNH1338
```

2. Frontend Setup:

```bash
cd fe
npm install
npm run dev
```

3. Backend Setup:

```bash
cd app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

4. Using Docker:

```bash
docker-compose up --build
```

### Project Structure

```
XDHTQLNH1338/
├── fe/                 # Frontend React application
│   ├── src/           # Source code
│   ├── public/        # Static files
│   └── package.json   # Dependencies
│
└── app/               # Backend Django application
    ├── web_01/        # Main web application
    ├── authentication/# Authentication module
    ├── core/          # Core functionality
    ├── mysocket/      # WebSocket handling
    └── requirements.txt
```

### Features

- Real-time updates using WebSocket
- JWT Authentication
- Internationalization support
- PDF generation
- QR code generation
- Cloud storage integration
- API documentation with Swagger/OpenAPI

### Development

- Frontend runs on: http://localhost:5173
- Backend runs on: http://localhost:8000
- API documentation: http://localhost:8000/api/docs/

### Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### License

This project is licensed under the terms of the license included in the repository.

---

## Tiếng Việt

### Tổng quan

Đây là ứng dụng web full-stack được xây dựng bằng React (Frontend) và Django (Backend). Ứng dụng có các tính năng thời gian thực, xác thực và nhiều tích hợp khác.

### Công nghệ sử dụng

#### Frontend

- React 18
- Vite
- Material-UI & Bootstrap
- React Query
- i18next (Đa ngôn ngữ)
- Styled Components & SASS
- Các tiện ích (Tạo PDF, mã QR, v.v.)

#### Backend

- Django 5.1.3
- Django REST Framework
- Django Channels (WebSocket)
- Redis
- Xác thực JWT
- Lưu trữ đám mây (Cloudinary)
- Hỗ trợ Docker

### Yêu cầu hệ thống

- Node.js (v16 trở lên)
- Python 3.8 trở lên
- Docker và Docker Compose
- Redis

### Cài đặt

1. Clone repository:

```bash
git clone [repository-url]
cd XDHTQLNH1338
```

2. Cài đặt Frontend:

```bash
cd fe
npm install
npm run dev
```

3. Cài đặt Backend:

```bash
cd app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

4. Sử dụng Docker:

```bash
docker-compose up --build
```

### Cấu trúc dự án

```
XDHTQLNH1338/
├── fe/                 # Ứng dụng React Frontend
│   ├── src/           # Mã nguồn
│   ├── public/        # Tệp tĩnh
│   └── package.json   # Dependencies
│
└── app/               # Ứng dụng Django Backend
    ├── web_01/        # Ứng dụng web chính
    ├── authentication/# Module xác thực
    ├── core/          # Chức năng cốt lõi
    ├── mysocket/      # Xử lý WebSocket
    └── requirements.txt
```

### Tính năng

- Cập nhật thời gian thực sử dụng WebSocket
- Xác thực JWT
- Hỗ trợ đa ngôn ngữ
- Tạo PDF
- Tạo mã QR
- Tích hợp lưu trữ đám mây
- Tài liệu API với Swagger/OpenAPI

### Phát triển

- Frontend chạy tại: http://localhost:5173
- Backend chạy tại: http://localhost:8000
- Tài liệu API: http://localhost:8000/api/docs/

### Đóng góp

1. Fork repository
2. Tạo nhánh tính năng
3. Commit các thay đổi
4. Push lên nhánh
5. Tạo Pull Request

### Giấy phép

Dự án này được cấp phép theo các điều khoản của giấy phép được bao gồm trong repository.
