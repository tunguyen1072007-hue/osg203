"""
Chương trình Quản lý Ma trận Tài nguyên Hệ thống (Resource Matrix Management)
Bao gồm các ma trận: Allocation, Max, Available, Need và Thuật toán Banker (Deadlock Avoidance)
"""

import copy
import sys

# Đảm bảo in tiếng Việt có dấu trên Windows console mà không bị lỗi mã hóa
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


class ResourceManager:
    def __init__(self, num_processes=0, num_resources=0):
        self.n = num_processes  # Số tiến trình
        self.m = num_resources  # Số loại tài nguyên
        self.processes = []     # Danh sách nhãn tiến trình (VD: P0, P1, ...)
        self.resources = []     # Danh sách nhãn tài nguyên (VD: A, B, C, ...)
        self.allocation = []    # Ma trận Allocation (n x m)
        self.max_matrix = []    # Ma trận Max (n x m)
        self.available = []     # Vector Available (1 x m)
        self.need = []          # Ma trận Need (n x m) = Max - Allocation

    def load_sample_data(self):
        """
        Nạp dữ liệu mẫu kinh điển (Theo giáo trình Hệ điều hành - Silberschatz):
        5 tiến trình (P0 - P4) và 3 loại tài nguyên (A, B, C)
        """
        self.n = 5
        self.m = 3
        self.processes = [f"P{i}" for i in range(self.n)]
        self.resources = ["A", "B", "C"]

        self.allocation = [
            [0, 1, 0],  # P0
            [2, 0, 0],  # P1
            [3, 0, 2],  # P2
            [2, 1, 1],  # P3
            [0, 0, 2]   # P4
        ]

        self.max_matrix = [
            [7, 5, 3],  # P0
            [3, 2, 2],  # P1
            [9, 0, 2],  # P2
            [2, 2, 2],  # P3
            [4, 3, 3]   # P4
        ]

        self.available = [3, 3, 2]
        self.calculate_need()
        print("\n[+] Đã tải dữ liệu mẫu chuẩn thành công!")

    def calculate_need(self):
        """
        Tính toán ma trận Need: Need[i][j] = Max[i][j] - Allocation[i][j]
        """
        self.need = []
        for i in range(self.n):
            row = []
            for j in range(self.m):
                val = self.max_matrix[i][j] - self.allocation[i][j]
                if val < 0:
                    raise ValueError(f"Lỗi logic: Allocation[{self.processes[i]}][{self.resources[j]}] > Max")
                row.append(val)
            self.need.append(row)

    def input_custom_data(self):
        """Nhập dữ liệu tùy biến từ bàn phím với kiểm tra hợp lệ"""
        print("\n--- NHẬP DỮ LIỆU HỆ THỐNG MỚI ---")
        try:
            self.n = int(input("Nhập số lượng tiến trình (n): "))
            self.m = int(input("Nhập số loại tài nguyên (m): "))
            if self.n <= 0 or self.m <= 0:
                print("[-] Số lượng phải lớn hơn 0.")
                return False

            self.processes = [f"P{i}" for i in range(self.n)]
            self.resources = [chr(65 + i) if i < 26 else f"R{i}" for i in range(self.m)]

            print(f"\nTiến trình: {', '.join(self.processes)}")
            print(f"Tài nguyên: {', '.join(self.resources)}")

            # Nhập Allocation
            print(f"\n1. Nhập ma trận ALLOCATION ({self.n} dòng, mỗi dòng {self.m} số cách nhau bởi khoảng trắng):")
            self.allocation = []
            for i in range(self.n):
                while True:
                    line = input(f"  {self.processes[i]}: ").strip().split()
                    if len(line) == self.m and all(x.isdigit() for x in line):
                        self.allocation.append([int(x) for x in line])
                        break
                    print(f"  [!] Vui lòng nhập đúng {self.m} số nguyên không âm.")

            # Nhập Max
            print(f"\n2. Nhập ma trận MAX ({self.n} dòng, mỗi dòng {self.m} số cách nhau bởi khoảng trắng):")
            self.max_matrix = []
            for i in range(self.n):
                while True:
                    line = input(f"  {self.processes[i]}: ").strip().split()
                    if len(line) == self.m and all(x.isdigit() for x in line):
                        row = [int(x) for x in line]
                        # Kiểm tra Max >= Allocation
                        if any(row[j] < self.allocation[i][j] for j in range(self.m)):
                            print(f"  [!] Max không được nhỏ hơn Allocation tương ứng!")
                            continue
                        self.max_matrix.append(row)
                        break
                    print(f"  [!] Vui lòng nhập đúng {self.m} số nguyên không âm.")

            # Nhập Available
            print(f"\n3. Nhập vector AVAILABLE ({self.m} số cách nhau bởi khoảng trắng):")
            while True:
                line = input(f"  Available: ").strip().split()
                if len(line) == self.m and all(x.isdigit() for x in line):
                    self.available = [int(x) for x in line]
                    break
                print(f"  [!] Vui lòng nhập đúng {self.m} số nguyên không âm.")

            self.calculate_need()
            print("\n[+] Đã khởi tạo và tính ma trận Need thành công!")
            return True
        except Exception as e:
            print(f"[-] Có lỗi xảy ra trong quá trình nhập: {e}")
            return False

    def display_matrices(self):
        """Hiển thị tất cả ma trận tài nguyên dưới dạng bảng trực quan"""
        if self.n == 0 or self.m == 0:
            print("[-] Chưa có dữ liệu ma trận. Vui lòng nạp hoặc nhập dữ liệu!")
            return

        print("\n" + "=" * 76)
        print(" BẢNG TỔNG HỢP MA TRẬN TÀI NGUYÊN HỆ THỐNG ".center(76, "-"))
        print("=" * 76)

        res_header = " ".join([f"{r:>3}" for r in self.resources])
        
        # Header
        col1 = "Tiến trình"
        print(f"{col1:<12} | {'ALLOCATION':^{len(res_header)}} | {'MAX':^{len(res_header)}} | {'NEED':^{len(res_header)}} | AVAILABLE")
        print(f"{'':<12} | {res_header} | {res_header} | {res_header} | {res_header}")
        print("-" * 76)

        for i in range(self.n):
            alloc_str = " ".join([f"{self.allocation[i][j]:>3}" for j in range(self.m)])
            max_str   = " ".join([f"{self.max_matrix[i][j]:>3}" for j in range(self.m)])
            need_str  = " ".join([f"{self.need[i][j]:>3}" for j in range(self.m)])

            # Dòng đầu tiên in vector Available
            if i == 0:
                avail_str = " ".join([f"{self.available[j]:>3}" for j in range(self.m)])
            else:
                avail_str = ""

            print(f"{self.processes[i]:<12} | {alloc_str} | {max_str} | {need_str} | {avail_str}")

        print("=" * 76)
        print(f"Công thức tính: Need[i][j] = Max[i][j] - Allocation[i][j]\n")

    def check_safety(self, verbose=True):
        """
        Thuật toán kiểm tra trạng thái an toàn (Banker's Safety Algorithm)
        Trả về: (is_safe: bool, safe_sequence: list)
        """
        if self.n == 0:
            print("[-] Chưa có dữ liệu ma trận!")
            return False, []

        work = copy.deepcopy(self.available)
        finish = [False] * self.n
        safe_sequence = []

        if verbose:
            print("\n" + "-" * 60)
            print(" KIỂM TRA TRẠNG THÁI AN TOÀN (SAFETY ALGORITHM) ".center(60, "="))
            print(f"Work ban đầu = Available = {work}")
            print("-" * 60)

        step = 1
        while len(safe_sequence) < self.n:
            found = False
            for i in range(self.n):
                if not finish[i]:
                    # Kiểm tra Need[i] <= Work
                    can_allocate = True
                    for j in range(self.m):
                        if self.need[i][j] > work[j]:
                            can_allocate = False
                            break

                    if can_allocate:
                        # Giả định tiến trình i hoàn thành và trả lại tài nguyên
                        old_work = copy.deepcopy(work)
                        for j in range(self.m):
                            work[j] += self.allocation[i][j]
                        finish[i] = True
                        safe_sequence.append(self.processes[i])
                        found = True

                        if verbose:
                            need_i = self.need[i]
                            alloc_i = self.allocation[i]
                            print(f"Bước {step}: Chọn tiến trình {self.processes[i]}")
                            print(f"  + Điều kiện thỏa: Need {need_i} <= Work {old_work}")
                            print(f"  + Work mới = Work cũ + Allocation = {old_work} + {alloc_i} = {work}")
                            print(f"  + Finish[{self.processes[i]}] = True\n")
                            step += 1
                        break

            if not found:
                break

        is_safe = all(finish)
        if verbose:
            print("-" * 60)
            if is_safe:
                print(" KẾT LUẬN: Hệ thống ở TRẠNG THÁI AN TOÀN (SAFE STATE) ")
                print(f" Chuỗi an toàn (Safe Sequence): < {' -> '.join(safe_sequence)} >")
            else:
                deadlocked = [self.processes[i] for i in range(self.n) if not finish[i]]
                print(" KẾT LUẬN: Hệ thống ở TRẠNG THÁI KHÔNG AN TOÀN (UNSAFE STATE) ")
                print(f" Nguy cơ dẫn đến Deadlock! Các tiến trình bị nghẽn: {', '.join(deadlocked)}")
            print("-" * 60 + "\n")

        return is_safe, safe_sequence

    def request_resources(self, p_index, request):
        """
        Thuật toán yêu cầu cấp phát tài nguyên (Resource-Request Algorithm)
        """
        p_name = self.processes[p_index]
        print(f"\n--- XỬ LÝ YÊU CẦU CẤP PHÁT CHO {p_name} ---")
        print(f"Vector yêu cầu Request = {request}")

        # Bước 1: Kiểm tra Request <= Need
        for j in range(self.m):
            if request[j] > self.need[p_index][j]:
                print(f"[-] LỖI (BƯỚC 1): {p_name} yêu cầu vượt quá nhu cầu tối đa đã khai báo!")
                print(f"    Tại tài nguyên {self.resources[j]}: Request ({request[j]}) > Need ({self.need[p_index][j]})")
                return False

        # Bước 2: Kiểm tra Request <= Available
        for j in range(self.m):
            if request[j] > self.available[j]:
                print(f"[!] THÔNG BÁO (BƯỚC 2): Không đủ tài nguyên khả dụng. {p_name} phải chờ (Wait)!")
                print(f"    Tại tài nguyên {self.resources[j]}: Request ({request[j]}) > Available ({self.available[j]})")
                return False

        print("[+] Bước 1 & Bước 2 hợp lệ: Đang thử nghiệm cấp phát giả định...")

        # Bước 3: Cấp phát giả định
        # Lưu lại trạng thái cũ đề phòng rollback
        old_available = copy.deepcopy(self.available)
        old_allocation = copy.deepcopy(self.allocation)
        old_need = copy.deepcopy(self.need)

        for j in range(self.m):
            self.available[j] -= request[j]
            self.allocation[p_index][j] += request[j]
            self.need[p_index][j] -= request[j]

        # Kiểm tra trạng thái an toàn
        is_safe, seq = self.check_safety(verbose=True)

        if is_safe:
            print(f"[+] THÀNH CÔNG: Yêu cầu của {p_name} ĐƯỢC CHẤP THUẬN!")
            print(f"    Hệ thống duy trì trạng thái an toàn với chuỗi: < {' -> '.join(seq)} >")
            return True
        else:
            # Khôi phục trạng thái cũ (Rollback)
            self.available = old_available
            self.allocation = old_allocation
            self.need = old_need
            print(f"[-] TỪ CHỐI: Cấp phát sẽ đưa hệ thống vào trạng thái KHÔNG AN TOÀN.")
            print(f"    Khôi phục trạng thái ban đầu. {p_name} phải chờ!")
            return False


def main():
    manager = ResourceManager()
    # Mặc định nạp dữ liệu mẫu để người dùng có thể test ngay
    manager.load_sample_data()

    while True:
        print("""
============================================================
   CHƯƠNG TRÌNH QUẢN LÝ MA TRẬN TÀI NGUYÊN HỆ THỐNG (OS)
============================================================
 1. Hiển thị các ma trận (Allocation, Max, Need, Available)
 2. Kiểm tra trạng thái an toàn (Banker's Safety Algorithm)
 3. Xử lý yêu cầu cấp phát tài nguyên mới (Resource-Request)
 4. Nhập dữ liệu ma trận mới từ bàn phím
 5. Nạp lại dữ liệu mẫu (Silberschatz Preset)
 0. Thoát chương trình
------------------------------------------------------------""")
        choice = input("Nhập lựa chọn của bạn (0-5): ").strip()

        if choice == "1":
            manager.display_matrices()
        elif choice == "2":
            manager.check_safety(verbose=True)
        elif choice == "3":
            if manager.n == 0:
                print("[-] Chưa có dữ liệu ma trận!")
                continue
            print(f"\nDanh sách tiến trình khả dụng: {', '.join([f'{i}: {manager.processes[i]}' for i in range(manager.n)])}")
            try:
                p_idx = int(input(f"Chọn chỉ số tiến trình (0 đến {manager.n - 1}): "))
                if p_idx < 0 or p_idx >= manager.n:
                    print("[-] Chỉ số tiến trình không hợp lệ!")
                    continue
                req_str = input(f"Nhập vector Request cho {manager.processes[p_idx]} ({manager.m} số, cách nhau khoảng trắng): ")
                req = [int(x) for x in req_str.strip().split()]
                if len(req) != manager.m:
                    print(f"[-] Vui lòng nhập đúng {manager.m} giá trị!")
                    continue
                manager.request_resources(p_idx, req)
            except ValueError:
                print("[-] Dữ liệu nhập vào phải là số nguyên!")
        elif choice == "4":
            manager.input_custom_data()
        elif choice == "5":
            manager.load_sample_data()
        elif choice == "0":
            print("\nĐã thoát chương trình. Tạm biệt!")
            break
        else:
            print("[-] Lựa chọn không hợp lệ, vui lòng chọn từ 0 đến 5.")

if __name__ == "__main__":
    main()
