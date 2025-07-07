import tkinter as tk
from tkinter import messagebox


class ButtonDemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("按钮点击演示")
        self.root.geometry("400x300")
        self.root.minsize(300, 250)

        # 设置中文字体
        self.style = ('SimHei', 10)

        # 点击计数
        self.click_count = 0

        self.create_widgets()

    def create_widgets(self):
        # 创建主框架
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题标签
        title_label = tk.Label(
            main_frame,
            text="按钮点击事件演示",
            font=('SimHei', 16, 'bold'),
            pady=10
        )
        title_label.pack()

        # 按钮容器
        button_frame = tk.Frame(main_frame, pady=20)
        button_frame.pack(fill=tk.X)

        # 创建按钮
        self.demo_button = tk.Button(
            button_frame,
            text="点击我",
            font=self.style,
            bg="#3B82F6",
            fg="white",
            padx=20,
            pady=10,
            command=self.on_button_click  # 绑定点击事件
        )
        self.demo_button.pack(pady=10)

        # 点击计数标签
        self.count_label = tk.Label(
            main_frame,
            text=f"点击次数: {self.click_count}",
            font=self.style
        )
        self.count_label.pack(pady=10)

        # 信息显示区域
        self.info_text = tk.Text(
            main_frame,
            height=4,
            width=40,
            font=self.style,
            wrap=tk.WORD
        )
        self.info_text.pack(fill=tk.X, pady=10)
        self.info_text.config(state=tk.DISABLED)

        # 按钮组
        option_frame = tk.Frame(main_frame)
        option_frame.pack(fill=tk.X, pady=10)

        # 改变按钮文本的按钮
        change_text_btn = tk.Button(
            option_frame,
            text="更改按钮文本",
            font=self.style,
            command=self.change_button_text
        )
        change_text_btn.pack(side=tk.LEFT, padx=5)

        # 重置计数的按钮
        reset_count_btn = tk.Button(
            option_frame,
            text="重置计数",
            font=self.style,
            command=self.reset_count
        )
        reset_count_btn.pack(side=tk.LEFT, padx=5)

    def on_button_click(self):
        """处理按钮点击事件"""
        self.click_count += 1

        # 更新计数标签
        self.count_label.config(text=f"点击次数: {self.click_count}")

        # 在信息区域显示消息
        self.update_info_text(f"按钮第 {self.click_count} 次被点击！")

        # 每点击5次改变按钮颜色
        if self.click_count % 5 == 0:
            self.change_button_color()

    def update_info_text(self, message):
        """更新信息显示区域"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, message)
        self.info_text.config(state=tk.DISABLED)

    def change_button_text(self):
        """更改按钮文本"""
        current_text = self.demo_button["text"]
        if current_text == "点击我":
            self.demo_button["text"] = "已点击"
        else:
            self.demo_button["text"] = "点击我"

        self.update_info_text("按钮文本已更改！")

    def change_button_color(self):
        """更改按钮颜色"""
        current_bg = self.demo_button["bg"]
        colors = ["#3B82F6", "#10B981", "#8B5CF6", "#EF4444", "#EAB308"]

        # 选择与当前颜色不同的下一个颜色
        current_index = colors.index(current_bg) if current_bg in colors else -1
        next_index = (current_index + 1) % len(colors)

        self.demo_button["bg"] = colors[next_index]
        self.update_info_text(f"按钮颜色已更改为 {colors[next_index]}！")

    def reset_count(self):
        """重置点击计数"""
        if messagebox.askyesno("确认", "确定要重置计数吗？"):
            self.click_count = 0
            self.count_label.config(text=f"点击次数: {self.click_count}")
            self.update_info_text("点击计数已重置为0！")


if __name__ == "__main__":
    root = tk.Tk()
    app = ButtonDemoApp(root)
    root.mainloop()