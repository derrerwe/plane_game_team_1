# #窗口按钮放置
# import tkinter as tk
# from tkinter import messagebox
# from PIL import Image, ImageTk  # 用于处理图片
# import os
#
#
# class ButtonExampleApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("高级按钮示例")
#         self.root.geometry("600x400")
#         self.root.configure(bg="#f0f0f0")
#
#         # 创建主框架
#         main_frame = tk.Frame(root, bg="#f0f0f0")
#         main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
#
#         # 创建标题
#         title_label = tk.Label(
#             main_frame,
#             text="按钮功能演示",
#             font=("Arial", 16, "bold"),
#             bg="#f0f0f0",
#             fg="#333333"
#         )
#         title_label.pack(pady=(0, 20))
#
#         # === 文本按钮区域 ===
#         text_frame = tk.LabelFrame(main_frame, text="文本按钮", bg="#f0f0f0", padx=10, pady=10)
#         text_frame.pack(fill=tk.X, pady=10)
#
#         # 普通按钮
#         self.normal_button = tk.Button(
#             text_frame,
#             text="普通按钮",
#             command=self.on_normal_button_click,
#             bg="#4CAF50",
#             fg="white",
#             font=("Arial", 10),
#             padx=15,
#             pady=5
#         )
#         self.normal_button.pack(side=tk.LEFT, padx=5)
#
#         # 禁用按钮
#         self.disabled_button = tk.Button(
#             text_frame,
#             text="禁用按钮",
#             state=tk.DISABLED,
#             bg="#cccccc",
#             fg="#999999",
#             font=("Arial", 10),
#             padx=15,
#             pady=5
#         )
#         self.disabled_button.pack(side=tk.LEFT, padx=5)
#
#         # 切换状态按钮
#         self.toggle_var = tk.BooleanVar(value=False)
#         self.toggle_button = tk.Button(
#             text_frame,
#             text="开关关闭",
#             command=self.on_toggle_button_click,
#             bg="#f44336",
#             fg="white",
#             font=("Arial", 10),
#             padx=15,
#             pady=5
#         )
#         self.toggle_button.pack(side=tk.LEFT, padx=5)
#
#         # === 图片按钮区域 ===
#         image_frame = tk.LabelFrame(main_frame, text="图片按钮", bg="#f0f0f0", padx=10, pady=10)
#         image_frame.pack(fill=tk.X, pady=10)
#
#         # 加载图片
#         try:
#             # 如果有实际图片文件，可以使用以下代码
#             # self.original_img = Image.open("button_image.png").resize((100, 40))
#             # 没有图片时使用空白图片
#             self.original_img = Image.new("RGBA", (100, 40), (66, 133, 244, 255))
#             self.hover_img = Image.new("RGBA", (100, 40), (52, 101, 164, 255))
#             self.disabled_img = Image.new("RGBA", (100, 40), (192, 192, 192, 255))
#
#             # 转换为Tkinter可用的格式
#             self.button_img = ImageTk.PhotoImage(self.original_img)
#             self.hover_button_img = ImageTk.PhotoImage(self.hover_img)
#             self.disabled_button_img = ImageTk.PhotoImage(self.disabled_img)
#
#             # 创建图片按钮
#             self.image_button = tk.Button(
#                 image_frame,
#                 image=self.button_img,
#                 command=self.on_image_button_click,
#                 borderwidth=0,
#                 relief=tk.FLAT
#             )
#             self.image_button.image = self.button_img  # 保持引用，防止被垃圾回收
#             self.image_button.pack(side=tk.LEFT, padx=5)
#
#             # 绑定鼠标事件
#             self.image_button.bind("<Enter>", self.on_enter_image_button)
#             self.image_button.bind("<Leave>", self.on_leave_image_button)
#
#             # 禁用的图片按钮
#             self.disabled_image_button = tk.Button(
#                 image_frame,
#                 image=self.disabled_button_img,
#                 state=tk.DISABLED,
#                 borderwidth=0,
#                 relief=tk.FLAT
#             )
#             self.disabled_image_button.image = self.disabled_button_img
#             self.disabled_image_button.pack(side=tk.LEFT, padx=5)
#
#         except Exception as e:
#             print(f"加载图片时出错: {e}")
#             # 创建文本替代图片按钮
#             tk.Label(image_frame, text="图片按钮加载失败", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
#
#         # === 特殊按钮区域 ===
#         special_frame = tk.LabelFrame(main_frame, text="特殊按钮", bg="#f0f0f0", padx=10, pady=10)
#         special_frame.pack(fill=tk.X, pady=10)
#
#         # 自定义样式按钮
#         self.custom_button = tk.Button(
#             special_frame,
#             text="自定义按钮",
#             command=self.on_custom_button_click,
#             bg="#FF9800",
#             fg="white",
#             font=("Arial", 10, "bold"),
#             padx=15,
#             pady=5,
#             relief=tk.RAISED,
#             bd=3,
#             highlightbackground="#FF5722",
#             highlightthickness=2
#         )
#         self.custom_button.pack(side=tk.LEFT, padx=5)
#
#         # 退出按钮
#         self.quit_button = tk.Button(
#             special_frame,
#             text="退出程序",
#             command=root.destroy,
#             bg="#f44336",
#             fg="white",
#             font=("Arial", 12),
#             padx=20,
#             pady=8
#         )
#         self.quit_button.pack(side=tk.RIGHT, padx=5)
#
#         # 状态标签
#         self.status_label = tk.Label(
#             main_frame,
#             text="等待操作...",
#             font=("Arial", 10),
#             bg="#f0f0f0",
#             fg="#666666"
#         )
#         self.status_label.pack(pady=20)
#
#     def on_normal_button_click(self):
#         """普通按钮点击事件处理"""
#         messagebox.showinfo("提示", "普通按钮被点击！")
#         self.status_label.config(text="普通按钮被点击")
#
#     def on_toggle_button_click(self):
#         """切换按钮点击事件处理"""
#         self.toggle_var.set(not self.toggle_var.get())
#         if self.toggle_var.get():
#             self.toggle_button.config(text="开关打开", bg="#4CAF50")
#             self.status_label.config(text="切换按钮状态：ON")
#         else:
#             self.toggle_button.config(text="开关关闭", bg="#f44336")
#             self.status_label.config(text="切换按钮状态：OFF")
#
#     def on_image_button_click(self):
#         """图片按钮点击事件处理"""
#         messagebox.showinfo("提示", "图片按钮被点击！")
#         self.status_label.config(text="图片按钮被点击")
#
#     def on_enter_image_button(self, event):
#         """鼠标进入图片按钮时的处理"""
#         self.image_button.config(image=self.hover_button_img)
#
#     def on_leave_image_button(self, event):
#         """鼠标离开图片按钮时的处理"""
#         self.image_button.config(image=self.button_img)
#
#     def on_custom_button_click(self):
#         """自定义按钮点击事件处理"""
#         messagebox.showinfo("提示", "自定义按钮被点击！")
#         self.status_label.config(text="自定义按钮被点击")
#
#
# if __name__ == "__main__":
#     # 确保中文显示正常
#     root = tk.Tk()
#
#     # 如果需要加载实际图片，取消下面的注释并提供图片路径
#     # try:
#     #     import matplotlib.pyplot as plt
#     #     plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
#     # except:
#     #     pass
#
#     app = ButtonExampleApp(root)
#     root.mainloop()
import tkinter as tk


class AnimatedModeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("动画模式切换")
        self.root.geometry("600x400")

        # 游戏模式
        self.NORMAL_MODE = 0
        self.MINING_MODE = 1
        self.current_mode = self.NORMAL_MODE
        self.is_changing_mode = False  # 模式切换中标志

        # 创建游戏画布
        self.canvas = tk.Canvas(root, width=600, height=300, bg="black")
        self.canvas.pack(pady=10)

        # 创建模式切换按钮
        self.mode_button = tk.Button(
            root,
            text="切换到采矿模式",
            command=self.toggle_mode,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            state=tk.NORMAL
        )
        self.mode_button.pack(pady=5)

        # 创建状态显示
        self.status_label = tk.Label(
            root,
            text="当前模式: 战斗模式",
            font=("Arial", 14),
            bg="#f0f0f0"
        )
        self.status_label.pack(pady=5)

        # 游戏元素
        self.player = self.canvas.create_rectangle(280, 250, 320, 270, fill="blue")
        self.mode_overlay = self.canvas.create_rectangle(0, 0, 600, 300, fill="black", state=tk.HIDDEN)

        # 启动游戏循环
        self.game_loop()

    def toggle_mode(self):
        """切换游戏模式（带动画效果）"""
        if self.is_changing_mode:
            return  # 正在切换中，不响应

        self.is_changing_mode = True
        self.mode_button.config(state=tk.DISABLED)  # 禁用按钮

        # 显示过
        self.canvas.itemconfig(self.mode_overlay, state=tk.NORMAL)
        self.canvas.itemconfig(self.mode_overlay, fill="black")

        # 淡出动画
        alpha = 0
        self.fade_out(alpha)

    def fade_out(self, alpha):
        """淡出动画"""
        alpha += 10
        if alpha > 200:
            # 切换模式
            if self.current_mode == self.NORMAL_MODE:
                self.current_mode = self.MINING_MODE
                self.status_label.config(text="当前模式: 采矿模式")
                self.mode_button.config(text="切换到战斗模式")
            else:
                self.current_mode = self.NORMAL_MODE
                self.status_label.config(text="当前模式: 战斗模式")
                self.mode_button.config(text="切换到采矿模式")

            # 开始淡入动画
            self.fade_in(200)
            return

        # 更新遮罩透明度（通过颜色模拟）
        color = f"#{int(alpha):02x}{int(alpha):02x}{int(alpha):02x}"
        self.canvas.itemconfig(self.mode_overlay, fill=color)
        self.root.after(10, lambda: self.fade_out(alpha))

    def fade_in(self, alpha):
        """淡入动画"""
        alpha -= 10
        if alpha < 0:
            self.canvas.itemconfig(self.mode_overlay, state=tk.HIDDEN)
            self.is_changing_mode = False
            self.mode_button.config(state=tk.NORMAL)  # 重新启用按钮
            return

        color = f"#{int(alpha):02x}{int(alpha):02x}{int(alpha):02x}"
        self.canvas.itemconfig(self.mode_overlay, fill=color)
        self.root.after(10, lambda: self.fade_in(alpha))

    def game_loop(self):
        """游戏主循环"""
        if not self.is_changing_mode:  # 切换模式时不更新游戏
            if self.current_mode == self.NORMAL_MODE:
                self.update_combat()
            else:
                self.update_mining()

        self.root.after(30, self.game_loop)

    def update_combat(self):
        """战斗模式更新"""
        self.canvas.delete("enemy")
        import random
        if random.randint(1, 100) < 3:
            x = random.randint(50, 550)
            self.canvas.create_oval(x, 20, x + 20, 40, fill="red", tags="enemy")

    def update_mining(self):
        """采矿模式更新"""
        self.canvas.delete("mineral")
        import random
        if random.randint(1, 100) < 5:
            x = random.randint(50, 550)
            self.canvas.create_oval(x, 20, x + 15, 35, fill="yellow", tags="mineral")


if __name__ == "__main__":
    root = tk.Tk()
    game = AnimatedModeGame(root)
    root.mainloop()