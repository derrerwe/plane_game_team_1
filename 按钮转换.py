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

        # 显示过渡遮罩
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