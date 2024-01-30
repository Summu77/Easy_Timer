import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime, timedelta
import sqlite3

class TimeManagementApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Summu77's timer")
        self.root.geometry("1000x600")

        # 数据库1 用于实现功能1
        self.conn = sqlite3.connect('time_management.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
                   CREATE TABLE IF NOT EXISTS plans (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       text TEXT NOT NULL,
                       checked BOOLEAN NOT NULL,
                       date DATE NOT NULL
                   )
               ''')
        self.conn.commit()

        # 数据库2 用于实现功能2
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS study_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time DATETIME,
                        end_time DATETIME,
                        date DATE
                    )
                ''')
        self.conn.commit()


        self.total_study_time = timedelta()

        # 创建左侧边栏
        self.sidebar = ttk.Frame(self.root, width=200, padding=(10, 10, 0, 10))
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        # 创建右侧内容区域
        self.content_frame = ttk.Frame(self.root, padding=(10, 10, 10, 10))
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # 初始化默认页面
        self.default_page()

        # 添加左侧功能按钮
        self.add_sidebar_buttons()
        self.plan_items = []  # 添加这行来初始化计划项列表

    def __del__(self):
        # 关闭数据库连接
        self.conn.close()

    def default_page(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # 标题标签
        title_label = ttk.Label(self.content_frame, text="欢迎使用 Summu77's timer 时间管理软件！",
                                font=("Helvetica", 16))
        title_label.grid(row=0, column=0, pady=10, columnspan=2, sticky="n")

        # 五点介绍文本
        intro_text = """
        1. 制定计划：在左侧边栏点击“制定计划”按钮，规划您的任务计划。
        2. 开始时间计时：点击“开始时间计时”按钮，开始任务计时器，提高效率。
        3. 今日复盘总结：使用“今日复盘总结”功能，总结您的一天，为明天做准备。
        4. 界面美观：我们注重界面设计，提供良好的使用体验。
        5. 简单实用：Summu77's timer 致力于为用户提供简单、实用的时间管理功能。
        """

        intro_textbox = tk.Text(self.content_frame, wrap="none", height=10
                                , width=95, font=("Helvetica", 12))
        intro_textbox.insert("1.0", intro_text)
        intro_textbox.config(state="disabled", wrap="none")

        # 设置文本居中显示
        # intro_textbox.tag_configure("center", justify="center")
        # intro_textbox.tag_add("center", "1.0", "end")

        intro_textbox.grid(row=1, column=0, pady=10, columnspan=2, sticky="n", ipady=5, padx=5)

    def add_sidebar_buttons(self):
        # 制定计划按钮
        plan_button = ttk.Button(self.sidebar, text="制定计划", command=self.show_plan_page)
        plan_button.grid(row=0, column=0, pady=10, padx=5, sticky="ew")

        # 开始时间计时按钮
        timer_button = ttk.Button(self.sidebar, text="开始计时", command=self.show_timer_page)
        timer_button.grid(row=1, column=0, pady=10, padx=5, sticky="ew")

        # 今日复盘总结按钮
        summary_button = ttk.Button(self.sidebar, text="复盘总结", command=self.show_summary_page)
        summary_button.grid(row=2, column=0, pady=10, padx=5, sticky="ew")

        summary_button = ttk.Button(self.sidebar, text="初始页面", command=self.default_page)
        summary_button.grid(row=3, column=0, pady=10, padx=5, sticky="ew")

# ----------------------------------plan part------------------------------------

    def show_plan_page(self):
        # 清空右侧内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 标题标签
        title_label = ttk.Label(self.content_frame, text="Let's make a plan for today！", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, pady=10, columnspan=3, sticky="n")

        # 显示当前日期和剩余时间
        self.remaining_label = ttk.Label(self.content_frame, text="", font=("Helvetica", 12))
        self.remaining_label.grid(row=1, column=0, pady=10, columnspan=3, sticky="n")

        # 实时更新剩余时间
        self.update_to_remaining_time()

        # 查询当天的计划
        today_date = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('SELECT * FROM plans WHERE date=?', (today_date,))
        plans = self.cursor.fetchall()

        # 显示插入计划的文本框和按钮
        plan_textbox = tk.Text(self.content_frame, wrap="word", height=2, width=95, font=("Helvetica", 12))
        plan_textbox.grid(row=2, column=0, pady=10, columnspan=3, sticky="n", ipady=5, padx=5)

        # 插入计划按钮
        insert_plan_button = ttk.Button(self.content_frame, text="插入计划",
                                        command=lambda: self.insert_plan(plan_textbox, today_date))
        insert_plan_button.grid(row=3, column=0, pady=10, columnspan=3, sticky="n")

        # 日期选择框
        date_label = ttk.Label(self.content_frame, text="选择日期：", font=("Helvetica", 12))
        date_label.grid(row=4, column=0, pady=10, sticky="e")

        self.selected_date = tk.StringVar()
        date_entry = ttk.Entry(self.content_frame, textvariable=self.selected_date, font=("Helvetica", 12))
        date_entry.grid(row=4, column=1, pady=10, sticky="nsew")

        # 查看历史计划按钮
        view_history_button = ttk.Button(self.content_frame, text="查看历史计划", command=self.view_history)
        view_history_button.grid(row=4, column=2, pady=10, sticky="w")

        # 显示当天的计划项
        for idx, plan in enumerate(plans, start=5):
            plan_item = {"id": plan[0], "text": plan[1], "checked": plan[2], "date": plan[3]}
            self.display_plan_item(plan_item, idx)

    def view_history(self):
        # 获取选择的日期
        selected_date = self.selected_date.get()

        if not selected_date:
            messagebox.showinfo("提示", "请选择日期，例如2022-02-28或28/02/2022")
            return

        # 查询选择日期的计划
        self.cursor.execute('SELECT * FROM plans WHERE date=?', (selected_date,))
        plans = self.cursor.fetchall()

        # 清空历史计划项
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.destroy()

        # 显示历史计划项
        for idx, plan in enumerate(plans, start=4):
            plan_item = {"id": plan[0], "text": plan[1], "checked": plan[2], "date": plan[3]}
            self.display_plan_item(plan_item, idx)

    def update_to_remaining_time(self):
        # 更新剩余时间标签
        current_date = datetime.now().strftime("%Y年%m月%d日")
        end_of_day = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        remaining_time = (end_of_day - datetime.now()).total_seconds() / 3600
        remaining_label_text = f"当前日期：{current_date}\n今日剩余：{remaining_time:.2f} 小时"
        self.remaining_label.config(text=remaining_label_text)

        # 每1000毫秒（1秒）更新一次剩余时间
        self.remaining_label.after(60000, self.update_remaining_time) # 一分钟更新一次

    def insert_plan(self, textbox, today_date):
        # 获取用户输入的计划
        plan_text = textbox.get("1.0", tk.END).strip()

        if plan_text:
            # 清空文本框
            textbox.delete("1.0", tk.END)

            # 将新计划插入数据库
            self.cursor.execute('INSERT INTO plans (text, checked, date) VALUES (?, ?, ?)',
                                (plan_text, False, today_date))
            self.conn.commit()

            # 查询当天的计划
            self.cursor.execute('SELECT * FROM plans WHERE date=?', (today_date,))
            plans = self.cursor.fetchall()

            # 显示插入计划后的计划项
            new_plan_item = {"id": plans[-1][0], "text": plans[-1][1], "checked": plans[-1][2], "date": plans[-1][3]}
            self.display_plan_item(new_plan_item, len(plans) + 3)

    def display_plan_item(self, plan_item, row):
        # 显示计划项
        plan_item_frame = ttk.Frame(self.content_frame)
        plan_item_frame.grid(row=row, column=0, pady=5, columnspan=3, sticky="w")

        # 复选框
        checkbox_var = tk.BooleanVar(value=plan_item["checked"])
        checkbox = ttk.Checkbutton(plan_item_frame, variable=checkbox_var,
                                   command=lambda: self.update_plan_checked(plan_item))
        checkbox.grid(row=0, column=0, padx=5)

        # 计划项文本
        plan_label = ttk.Label(plan_item_frame, text=plan_item["text"], font=("Helvetica", 12))
        plan_label.grid(row=0, column=1, padx=5, sticky="w")

        # 修改计划按钮
        edit_button = ttk.Button(plan_item_frame, text="修改",
                                 command=lambda: self.edit_plan(plan_label, checkbox_var, plan_item))
        edit_button.grid(row=0, column=2, padx=5, sticky="e")

        # 删除计划按钮
        delete_button = ttk.Button(plan_item_frame, text="删除",
                                   command=lambda: self.delete_plan(plan_item_frame, plan_item))
        delete_button.grid(row=0, column=3, padx=5, sticky="e")

    def update_plan_checked(self, plan_item):
        # 更新计划的完成状态
        new_checked_state = not plan_item["checked"]
        self.cursor.execute('UPDATE plans SET checked=? WHERE id=?', (new_checked_state, plan_item["id"]))
        self.conn.commit()

    def edit_plan(self, plan_label, checkbox_var, plan_item):
        # 弹出对话框让用户编辑计划
        edited_plan = simpledialog.askstring("编辑计划", "请输入修改后的计划", initialvalue=plan_item["text"])

        if edited_plan is not None:
            plan_label.config(text=edited_plan)
            plan_item["text"] = edited_plan
            self.cursor.execute('UPDATE plans SET text=? WHERE id=?', (edited_plan, plan_item["id"]))
            self.conn.commit()
            checkbox_var.set(False)  # 修改计划后将复选框重置为未选中状态

    def delete_plan(self, plan_frame, plan_item):
        # 删除计划项
        plan_frame.destroy()
        self.cursor.execute('DELETE FROM plans WHERE id=?', (plan_item["id"],))
        self.conn.commit()

# ----------------------------------timer part------------------------------------

    def show_timer_page(self):
        # 清空右侧内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 标题标签
        title_label = ttk.Label(self.content_frame, text="Let's study now！", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, pady=10, columnspan=3, sticky="n")

        # 初始化或者加载今天的时间表
        canvas = tk.Canvas(self.content_frame, width=800, height=370, bg="white")
        canvas.grid(row=1, column=0, pady=10, columnspan=3, sticky="n")
        self.draw_time_table(canvas)

        # 用户输入倒计时分钟数的Entry和开始倒计时按钮
        duration_label = ttk.Label(self.content_frame, text="设置学习时长（分钟）：", font=("Helvetica", 12))
        duration_label.grid(row=2, column=0, pady=10, sticky="e")
        self.duration_entry = ttk.Entry(self.content_frame, font=("Helvetica", 12))
        self.duration_entry.grid(row=2, column=1, pady=10, sticky="w")
        start_timer_button = ttk.Button(self.content_frame, text="开始倒计时", command=self.start_timer)
        start_timer_button.grid(row=2, column=2, pady=10)
        self.remaining_label = ttk.Label(self.content_frame, text="", font=("Helvetica", 12))
        self.remaining_label.grid(row=3, column=0, pady=10, columnspan=3, sticky="n")

        # 累计学习时长
        self.total_study_time_label = ttk.Label(self.content_frame, text="累计学习时间：00:00:00",
                                                font=("Helvetica", 12))
        self.total_study_time_label.grid(row=4, column=0, pady=10, columnspan=3, sticky="n")

    def start_timer(self):
        # 获取用户输入的倒计时分钟数
        try:
            duration_minutes = int(self.duration_entry.get())
        except ValueError:
            simpledialog.messagebox.showwarning("警告", "请输入有效的学习时长")
            return

        # 计算结束时间
        end_time = datetime.now() + timedelta(minutes=duration_minutes)

        # 在时间使用情况表中绘制颜色表示使用时间段
        self.color_time_slot(datetime.now(), end_time)

        # 更新剩余时间的显示
        self.update_remaining_time(end_time)

        # 更新累计学习时间的显示
        self.update_total_study_time()

        # 插入学习会话记录到数据库
        self.insert_study_session(datetime.now(), end_time)

    def insert_study_session(self, start_time, end_time):
        # 将开始时间和结束时间格式化为字符串
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        # 插入学习会话记录到数据库
        self.cursor.execute('INSERT INTO study_sessions (start_time, end_time, date) VALUES (?, ?, ?)',
                            (start_time_str, end_time_str, start_time.strftime('%Y-%m-%d')))
        self.conn.commit()

    def update_total_study_time(self):
        # 查询当天的学习会话记录
        today_date = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('SELECT start_time, end_time FROM study_sessions WHERE date=?', (today_date,))
        study_sessions = self.cursor.fetchall()

        # 计算当天学习时间的累计和
        total_study_time = timedelta()
        for session in study_sessions:
            start_time = datetime.strptime(session[0], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(session[1], '%Y-%m-%d %H:%M:%S')
            session_duration = end_time - start_time
            total_study_time += session_duration

        # 更新Label显示
        self.total_study_time_label.config(text=f"累计学习时间：{str(total_study_time).split('.')[0]}")

    def draw_time_table(self, canvas):

        # 绘制时间表格
        for hour in range(7, 25):
            y1 = (hour - 7) * 20 +5
            y2 = y1 + 20
            canvas.create_rectangle(10, y1, 800, y2, outline="black")

            # 显示几点的说明
            label_x = 10  # 说明文本的横坐标
            label_y = (y1 + y2) / 2  # 说明文本的纵坐标，取中间位置
            canvas.create_text(label_x, label_y, anchor=tk.W, text=f"{hour}:00", font=("Helvetica", 8))

        # 查询当天的学习会话记录
        today_date = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('SELECT start_time, end_time FROM study_sessions WHERE date=?', (today_date,))
        study_sessions = self.cursor.fetchall()

        # 遍历查询结果，并调用color_time_slot函数进行绘制
        for session in study_sessions:
            start_time = datetime.strptime(session[0], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(session[1], '%Y-%m-%d %H:%M:%S')
            self.color_time_slot(start_time, end_time)

    def update_remaining_time(self, end_time):
        # 计算剩余时间
        remaining_time = end_time - datetime.now()

        # 将剩余时间转换为只显示到秒的字符串
        remaining_time_str = str(remaining_time).split(".")[0]

        # 更新Label显示
        self.remaining_label.config(text=f"剩余时间：{remaining_time_str}")

        # 判断是否还需要继续更新
        if remaining_time > timedelta(0):
            self.root.after(1000, lambda: self.update_remaining_time(end_time))
        else:
            self.remaining_label.config(text="倒计时结束")

    def color_time_slot(self, current_time, end_time):

        canvas = self.content_frame.winfo_children()[1]

        if current_time.hour == end_time.hour:

            y1 = (current_time.hour - 7) * 20 + 6
            y2 = y1 + 19

            x1 = 10 + ( current_time.minute/60 ) * 790
            x2 = 10 + (end_time.minute / 60) * 790

            # 填充颜色
            canvas.create_rectangle(x1, y1, x2, y2, outline="", fill="lightblue")

        else :
            y1 = (current_time.hour - 7) * 20 + 6
            y2 = y1 + 19
            x1 = 10 + (current_time.minute / 60) * 790
            x2 = 10 + (60 / 60) * 790
            canvas.create_rectangle(x1, y1, x2, y2, outline="", fill="lightblue")

            y1 = (end_time.hour - 7) * 20 + 6
            y2 = y1 + 19
            x1 = 11
            x2 = 10 + (end_time.minute / 60) * 790
            canvas.create_rectangle(x1, y1, x2, y2, outline="", fill="lightblue")

# ----------------------------------summery part------------------------------------

    def show_summary_page(self):
        # 清空右侧内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        label = ttk.Label(self.content_frame, text="今日复盘总结页面", font=("Helvetica", 16))
        label.grid(row=0, column=0, pady=10, columnspan=3, sticky="n")

        # 显示当天的学习会话记录
        today_date = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('SELECT * FROM study_sessions WHERE date=?', (today_date,))
        study_sessions = self.cursor.fetchall()

        # 创建TreeView用于显示学习会话记录
        columns = ('ID', '开始时间', '结束时间')
        tree = ttk.Treeview(self.content_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)

        # 插入数据到TreeView中
        for session in study_sessions:
            tree.insert("", "end", values=session)

        tree.grid(row=1, column=0, columnspan=3, pady=10, sticky="nsew")

        # 创建按钮用于修改和删除记录
        modify_button = ttk.Button(self.content_frame, text="修改记录", command=lambda: self.modify_record(tree))
        modify_button.grid(row=2, column=0, pady=10, sticky="nsew")

        delete_button = ttk.Button(self.content_frame, text="删除记录", command=lambda: self.delete_record(tree))
        delete_button.grid(row=2, column=2, pady=10, sticky="nsew")

    def modify_record(self, tree):
        # 获取选中的记录
        selected_item = tree.selection()
        if selected_item:
            # 获取记录的ID
            record_id = tree.item(selected_item, 'values')[0]

            # 获取用户输入的新开始时间和新结束时间
            new_start_time = simpledialog.askstring("更新记录", "请输入新的开始时间 (YYYY-MM-DD HH:mm:ss):")
            new_end_time = simpledialog.askstring("更新记录", "请输入新的结束时间 (YYYY-MM-DD HH:mm:ss):")

            if new_start_time is not None and new_end_time is not None:
                # 更新记录
                self.cursor.execute('UPDATE study_sessions SET start_time=?, end_time=? WHERE id=?',
                                    (new_start_time, new_end_time, record_id))
                self.conn.commit()
                print(f"Record with ID {record_id} updated.")

                # 更新TreeView显示
                self.show_summary_page()

    def delete_record(self, tree):
        # 获取选中的记录
        selected_item = tree.selection()
        if selected_item:
            # 获取记录的ID
            record_id = tree.item(selected_item, 'values')[0]

            # 删除记录
            self.cursor.execute('DELETE FROM study_sessions WHERE id=?', (record_id,))
            self.conn.commit()
            print(f"Record with ID {record_id} deleted.")

            # 更新TreeView显示
            self.show_summary_page()


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeManagementApp(root)
    root.mainloop()
