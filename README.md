# Asteroids

A modern spin on the classic Asteroids arcade game, built using Python & Pygame. This project features intelligent enemy pathfinding algorithms, efficient collision detection using QuadTree, and a dynamic weapon upgrade system.

[English](#english-version) | [Tiếng Việt](#phiên-bản-tiếng-việt)

---

## English Version

### Features
* **Classic Gameplay:** Navigate your spaceship, destroy asteroids, and avoid collisions.
* **Intelligent AI:** Enemy saucers utilize advanced pathfinding algorithms (Weighted A* and BFS) to actively dodge obstacles and target the player.
* **Dynamic Weapon System:** Upgrade your firepower as you score points, unlocking powerful spread and burst firing modes.
* **Settings GUI:** Customize game parameters such as ship speed, enemy spawn rates, and difficulty directly from the built-in configuration menu.
* **High Score Tracking:** Compete for the top 10 positions on the local leaderboard.

### How to Download & Run

You can choose to run the game from the source code or use the pre-built standalone executable.

#### Option 1: Standalone Executable (Linux Only)
1. Go to the **Releases** page of this repository.
2. Download the latest `Asteroids` binary file.
3. Open a terminal in the download directory and make the file executable:
   ```bash
   chmod +x Asteroids
   ```
4. Run the game:
   ```bash
   ./Asteroids
   ```

#### Option 2: Running from Source
1. Clone the repository to your local machine:
   ```bash
   git clone <repository-url>
   cd asteroids
   ```
2. Ensure you have Python 3.8+ installed. Install the required dependencies:
   ```bash
   pip install pygame
   ```
3. Start the game:
   ```bash
   python3 src_own/main.py
   ```

### Controls
* **Up Arrow**: Thrust engine
* **Left / Right Arrows**: Rotate ship
* **Spacebar**: Standard fire
* **G**: Burst fire mode (Scales with weapon level)
* **S**: Hyperspace jump (Teleport to a random safe location)
* **P**: Pause / Resume
* **C**: Open Configuration Settings
* **M**: Mute / Unmute audio
* **F**: Toggle FPS counter
* **Q / Esc**: Quit game

---

## Phiên bản Tiếng Việt

### Tính năng Nổi bật
* **Lối chơi Cổ điển:** Điều khiển phi thuyền, phá hủy các thiên thạch và né tránh chướng ngại vật.
* **Trí tuệ Nhân tạo (AI):** Đĩa bay của kẻ địch sử dụng các thuật toán tìm đường tiên tiến (Weighted A* và BFS) để chủ động né tránh đạn và truy đuổi người chơi.
* **Hệ thống Vũ khí Động:** Vũ khí sẽ tự động được nâng cấp khi bạn đạt điểm cao, cho phép bắn tỏa và bắn chùm (burst mode) với hỏa lực mạnh mẽ.
* **Giao diện Cài đặt:** Tùy chỉnh trực tiếp các thông số trò chơi như tốc độ phi thuyền, tần suất xuất hiện kẻ địch và độ khó thông qua giao diện đồ họa.
* **Bảng Xếp hạng:** Hệ thống lưu trữ và xếp hạng top 10 điểm số cao nhất.

### Cách Tải và Chơi Game

Bạn có thể chạy trực tiếp bằng tệp thực thi (dành cho Linux) hoặc chạy qua mã nguồn Python.

#### Cách 1: Chạy Tệp Thực Thi (Chỉ hỗ trợ Linux)
1. Truy cập mục **Releases** trên repository này.
2. Tải xuống executable `Asteroids` mới nhất.
3. Mở terminal tại thư mục vừa tải về và cấp quyền:
   ```bash
   chmod +x Asteroids
   ```
4. Khởi chạy trò chơi:
   ```bash
   ./Asteroids
   ```

#### Cách 2: Chạy từ Mã nguồn (Đa nền tảng)
1. Tải (clone) mã nguồn về máy tính của bạn:
   ```bash
   git clone <repository-url>
   cd asteroids
   ```
2. Đảm bảo máy tính đã cài đặt Python 3.8 trở lên. Cài đặt các thư viện cần thiết:
   ```bash
   pip install pygame
   ```
3. Bắt đầu trò chơi:
   ```bash
   python3 src_own/main.py
   ```

### Phím Điều khiển
* **Mũi tên Lên**: Tăng tốc (Đẩy động cơ)
* **Mũi tên Trái / Phải**: Xoay phi thuyền
* **Dấu Cách (Space)**: Bắn đạn thường
* **Phím G**: Chế độ bắn chùm/tỏa (Sức mạnh tăng theo cấp độ vũ khí)
* **Phím S**: Bước nhảy không gian (Dịch chuyển tức thời đến một vị trí ngẫu nhiên)
* **Phím P**: Tạm dừng / Tiếp tục
* **Phím C**: Mở giao diện Cài đặt
* **Phím M**: Tắt / Mở âm thanh
* **Phím F**: Hiển thị thông số FPS
* **Phím Q / Esc**: Thoát trò chơi