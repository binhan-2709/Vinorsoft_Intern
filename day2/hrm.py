import os
from typing import List

# ========== DECORATOR ==========
# Decorator dùng để log khi gọi hàm
def log_action(func):
    def wrapper(*args, **kwargs):
        print(f"[LOG] Calling {func.__name__}...")  # In ra tên hàm đang chạy
        return func(*args, **kwargs)  # Gọi lại hàm gốc
    return wrapper

# ========== BASE CLASS ==========
# Lớp cơ bản Employee
class Employee:
    def __init__(self, name: str, salary: float):
        self.name = name
        self.salary = salary      

    # ========== PROPERTY ==========
    @property
    def salary(self) -> float:
        return self._salary       

    @salary.setter
    def salary(self, value: float):
        if value < 0:
            raise ValueError("Lương không được là số âm!")  
        self._salary = value      

    def get_salary(self) -> float:
        return self._salary      

    def __str__(self):
        return f"Employee: {self.name} | Salary: {self.get_salary()}"

    def to_file_str(self):
        return f"employee,{self.name},{self._salary}"

# ========== INHERITANCE ==========
# Manager kế thừa từ Employee
class Manager(Employee):
    def __init__(self, name: str, salary: float, bonus: float):
        super().__init__(name, salary)
        self.bonus = bonus

    def get_salary(self) -> float:
        return self._salary + self.bonus 

    def __str__(self):
        return f"Manager:  {self.name} | Salary: {self.get_salary()} (Base: {self._salary} + Bonus: {self.bonus})"

    def to_file_str(self):
        return f"manager,{self.name},{self._salary},{self.bonus}"

# Intern kế thừa Employee
class Intern(Employee):
    def get_salary(self) -> float:
        return self._salary * 0.5  

    def __str__(self):
        return f"Intern:   {self.name} | Salary: {self.get_salary()} (50% of {self._salary})"

    def to_file_str(self):
        return f"intern,{self.name},{self._salary}"

# ========== CONTEXT MANAGER ==========
# Dùng để quản lý file (tự động mở/đóng file)
class FileManager:
    def __init__(self, filename: str, mode: str = "w"):
        self.filename = filename
        self.mode = mode

    def __enter__(self):
        self.file = open(self.filename, self.mode, encoding="utf-8")  
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()  

# ========== INPUT HELPER ==========
def input_salary(prompt: str = "Salary: ") -> float:
    raw = input(prompt)
    try:
        value = float(raw)
    except ValueError:
        raise ValueError(f"'{raw}' không phải là số! Vui lòng nhập lại.")
    return value

# ========== HRM SYSTEM ==========
# Lớp quản lý toàn bộ nhân viên
class HRM:
    DEFAULT_FILE = "employees.txt"

    def __init__(self):
        self.employees: List[Employee] = []  

    def add_employee(self, emp: Employee):
        self.employees.append(emp)  

    def show_all(self):
        if not self.employees:
            print("No employees.")
            return
        print("-" * 55)
        for e in self.employees:
            print(e)  
        print("-" * 55)

    @log_action
    def total_salary(self):
        return sum(e.get_salary() for e in self.employees)

    def find_by_name(self, name: str):
        return [e for e in self.employees if e.name.lower() == name.lower()]

    def delete_by_name(self, name: str):
        before = len(self.employees)
        self.employees = [e for e in self.employees if e.name.lower() != name.lower()]
        return before - len(self.employees)

    # ========== GENERATOR ==========
    def employee_generator(self):
        for e in self.employees:
            yield e

    # ========== SAVE TO FILE ==========
    def save_to_file(self, filename=DEFAULT_FILE):
        with FileManager(filename, "w") as f:
            for e in self.employees:
                f.write(e.to_file_str() + "\n")
        print(f"✔ Đã lưu {len(self.employees)} nhân viên vào '{filename}'.")

    # ========== LOAD FROM FILE ==========
    def load_from_file(self, filename=DEFAULT_FILE):
        if not os.path.exists(filename):
            print(f"  (Chưa có file '{filename}', bắt đầu với danh sách trống.)")
            return

        loaded = 0
        errors = 0
        with FileManager(filename, "r") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                try:
                    emp_type = parts[0].lower()
                    if emp_type == "manager":
                        name, salary, bonus = parts[1], float(parts[2]), float(parts[3])
                        self.employees.append(Manager(name, salary, bonus))
                    elif emp_type == "intern":
                        name, salary = parts[1], float(parts[2])
                        self.employees.append(Intern(name, salary))
                    elif emp_type == "employee":
                        name, salary = parts[1], float(parts[2])
                        self.employees.append(Employee(name, salary))
                    else:
                        print(f"  [Dòng {line_num}] Loại không hợp lệ: '{emp_type}' — bỏ qua.")
                        errors += 1
                        continue
                    loaded += 1
                except (IndexError, ValueError) as e:
                    print(f"  [Dòng {line_num}] Lỗi đọc dữ liệu: {e} — bỏ qua.")
                    errors += 1

        print(f"✔ Đã tải {loaded} nhân viên từ '{filename}'." +
              (f" ({errors} dòng lỗi bị bỏ qua)" if errors else ""))

# ========== CONSOLE APP ==========
# Menu hiển thị chức năng
def menu():
    print("""
==== HRM SYSTEM ====
1. Add Employee
2. Show All
3. Total Salary
4. Find Employee
5. Delete Employee
6. Save to File
7. Load from File
0. Exit
""")

# Hàm main chạy chương trình
def main():
    hrm = HRM()
    print("=== Khởi động HRM System ===")

    while True:
        menu()
        choice = input("Choose: ").strip()

        if choice == "1":
            name = input("Name: ").strip()
            if not name:
                print("Tên không được để trống!")
                continue
            
            try:
                salary = input_salary("Salary: ")
            except ValueError as e:
                print(f"✖ {e}")
                continue

            valid_types = {"employee", "manager", "intern"}
            while True:
                emp_type = input("Type (employee/manager/intern): ").strip().lower()
                if emp_type in valid_types:
                    break
                print(f"✖ '{emp_type}' không hợp lệ! Vui lòng nhập: employee / manager / intern")

            try:
                if emp_type == "manager":
                    try:
                        bonus = input_salary("Bonus: ")
                    except ValueError as e:
                        print(f"✖ {e}")
                        continue
                    emp = Manager(name, salary, bonus)
                elif emp_type == "intern":
                    emp = Intern(name, salary)
                else:
                    emp = Employee(name, salary)
            except ValueError as e:
                print(f"✖ {e}")
                continue

            hrm.add_employee(emp)
            print(f"✔ Đã thêm: {emp}")

        elif choice == "2":
            hrm.show_all()

        elif choice == "3":
            total = hrm.total_salary()
            print(f"Total salary: {total:,.2f}")

        elif choice == "4":
            name = input("Enter name: ").strip()
            result = hrm.find_by_name(name)
            if result:
                for e in result:
                    print(e)
            else:
                print(f"Không tìm thấy nhân viên tên '{name}'.")

        elif choice == "5":
            name = input("Enter name to delete: ").strip()
            count = hrm.delete_by_name(name)
            if count:
                print(f"✔ Đã xóa {count} nhân viên tên '{name}'.")
            else:
                print(f"Không tìm thấy nhân viên tên '{name}'.")

        elif choice == "6":
            hrm.save_to_file()

        elif choice == "7":
            confirm = input("Load sẽ gộp thêm dữ liệu từ file. Tiếp tục? (y/n): ").strip().lower()
            if confirm == "y":
                hrm.load_from_file()
                if hrm.employees:
                    print("Danh sách nhân viên đã tải:")
                    hrm.show_all()

        elif choice == "0":
            print("Thoát chương trình. Tạm biệt!")
            break

        else:
            print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()