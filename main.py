"""游戏按键辅助 - 主界面。"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from config_manager import AppConfig, KeyAction, load_config, save_config
from macro_engine import HotkeyManager, MacroEngine

COMMON_KEYS = [
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
    "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
    "a", "s", "d", "f", "g", "h", "j", "k", "l",
    "z", "x", "c", "v", "b", "n", "m",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
    "space", "tab", "enter", "shift", "ctrl", "alt",
    "mouse left", "mouse right", "mouse middle",
]


class GameAssistantApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("游戏按键辅助")
        self.root.geometry("640x600")
        self.root.minsize(600, 540)

        self.config = load_config()
        self.engine = MacroEngine(on_state_change=self._on_engine_state_change)
        self.hotkey_manager = HotkeyManager()

        self._selected_index: int | None = None
        self._build_ui()
        self._refresh_action_list()
        self._register_hotkey()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # 顶部状态栏
        top = ttk.Frame(main)
        top.pack(fill=tk.X, pady=(0, 10))

        self.status_var = tk.StringVar(value="状态：已停止")
        ttk.Label(top, textvariable=self.status_var, font=("Microsoft YaHei UI", 11, "bold")).pack(
            side=tk.LEFT
        )

        self.toggle_btn = ttk.Button(top, text="开始 (F6)", command=self._toggle_macro)
        self.toggle_btn.pack(side=tk.RIGHT)

        # 热键设置
        hotkey_frame = ttk.LabelFrame(main, text="全局热键", padding=10)
        hotkey_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(hotkey_frame, text="启停热键：").grid(row=0, column=0, sticky=tk.W)
        self.hotkey_var = tk.StringVar(value=self.config.toggle_hotkey)
        hotkey_combo = ttk.Combobox(
            hotkey_frame,
            textvariable=self.hotkey_var,
            values=["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12", "`"],
            width=10,
            state="readonly",
        )
        hotkey_combo.grid(row=0, column=1, sticky=tk.W, padx=(4, 12))
        hotkey_combo.bind("<<ComboboxSelected>>", lambda _: self._apply_hotkey())

        ttk.Label(
            hotkey_frame,
            text="提示：游戏窗口需在前台；部分游戏可能拦截模拟按键，请以管理员身份运行。",
            foreground="#666666",
        ).grid(row=0, column=2, sticky=tk.W)

        # 中间：列表 + 按钮 + 编辑
        center = ttk.Frame(main)
        center.pack(fill=tk.BOTH, expand=True)

        list_frame = ttk.LabelFrame(center, text="按键列表", padding=8)
        list_frame.pack(fill=tk.BOTH, expand=True)

        tree_wrap = ttk.Frame(list_frame)
        tree_wrap.pack(fill=tk.BOTH, expand=True)

        columns = ("enabled", "key", "interval", "cast", "repeat")
        self.tree = ttk.Treeview(tree_wrap, columns=columns, show="headings", height=8)
        self.tree.heading("enabled", text="启用")
        self.tree.heading("key", text="按键")
        self.tree.heading("interval", text="间隔(ms)")
        self.tree.heading("cast", text="施法(ms)")
        self.tree.heading("repeat", text="次数")
        self.tree.column("enabled", width=50, anchor=tk.CENTER)
        self.tree.column("key", width=80, anchor=tk.CENTER)
        self.tree.column("interval", width=80, anchor=tk.CENTER)
        self.tree.column("cast", width=80, anchor=tk.CENTER)
        self.tree.column("repeat", width=70, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_wrap, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._on_select_action)

        list_btns = ttk.Frame(list_frame)
        list_btns.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(list_btns, text="添加", command=self._add_action).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(list_btns, text="删除", command=self._delete_action).pack(side=tk.LEFT)

        edit_frame = ttk.LabelFrame(list_frame, text="编辑按键", padding=12)
        edit_frame.pack(fill=tk.X, pady=(8, 0))

        self.enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(edit_frame, text="启用此按键", variable=self.enabled_var).grid(
            row=0, column=0, columnspan=6, sticky=tk.W, pady=(0, 8)
        )

        ttk.Label(edit_frame, text="按键：").grid(row=1, column=0, sticky=tk.W, pady=4, padx=(0, 4))
        self.key_var = tk.StringVar(value="1")
        key_combo = ttk.Combobox(edit_frame, textvariable=self.key_var, values=COMMON_KEYS, width=12)
        key_combo.grid(row=1, column=1, sticky=tk.W, pady=4, padx=(0, 16))

        ttk.Label(edit_frame, text="触发间隔(ms)：").grid(row=1, column=2, sticky=tk.W, pady=4, padx=(0, 4))
        self.interval_var = tk.StringVar(value="1000")
        ttk.Entry(edit_frame, textvariable=self.interval_var, width=10).grid(
            row=1, column=3, sticky=tk.W, pady=4, padx=(0, 16)
        )

        ttk.Label(edit_frame, text="重复次数：").grid(row=1, column=4, sticky=tk.W, pady=4, padx=(0, 4))
        self.repeat_var = tk.StringVar(value="0")
        ttk.Entry(edit_frame, textvariable=self.repeat_var, width=8).grid(
            row=1, column=5, sticky=tk.W, pady=4
        )

        ttk.Label(edit_frame, text="施法时间(ms)：").grid(row=2, column=0, sticky=tk.W, pady=4, padx=(0, 4))
        self.cast_var = tk.StringVar(value="100")
        ttk.Entry(edit_frame, textvariable=self.cast_var, width=12).grid(
            row=2, column=1, sticky=tk.W, pady=4, padx=(0, 16)
        )
        ttk.Label(edit_frame, text="按键按住时长，0 为瞬间按下", foreground="#666666").grid(
            row=2, column=2, columnspan=4, sticky=tk.W, pady=4
        )

        edit_bottom = ttk.Frame(edit_frame)
        edit_bottom.grid(row=3, column=0, columnspan=6, sticky=tk.EW, pady=(8, 0))
        edit_frame.columnconfigure(6, weight=1)

        ttk.Label(edit_bottom, text="0 = 无限循环", foreground="#666666").pack(side=tk.LEFT)
        ttk.Button(edit_bottom, text="保存修改", command=self._save_current_action).pack(side=tk.RIGHT)

        # 底部
        bottom = ttk.Frame(main)
        bottom.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(bottom, text="保存全部配置", command=self._save_all).pack(side=tk.RIGHT)
        ttk.Button(bottom, text="恢复默认", command=self._reset_default).pack(side=tk.RIGHT, padx=(0, 8))

    def _refresh_action_list(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, action in enumerate(self.config.actions):
            self.tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    "是" if action.enabled else "否",
                    action.key,
                    action.interval_ms,
                    action.cast_time_ms,
                    "无限" if action.repeat_count == 0 else action.repeat_count,
                ),
            )

    def _on_select_action(self, _event: tk.Event | None = None) -> None:
        selection = self.tree.selection()
        if not selection:
            self._selected_index = None
            return

        index = int(selection[0])
        self._selected_index = index
        action = self.config.actions[index]
        self.enabled_var.set(action.enabled)
        self.key_var.set(action.key)
        self.interval_var.set(str(action.interval_ms))
        self.cast_var.set(str(action.cast_time_ms))
        self.repeat_var.set(str(action.repeat_count))

    def _add_action(self) -> None:
        self.config.actions.append(KeyAction(key="1", interval_ms=1000))
        self._refresh_action_list()
        last_index = len(self.config.actions) - 1
        self.tree.selection_set(str(last_index))
        self.tree.focus(str(last_index))
        self._on_select_action()

    def _delete_action(self) -> None:
        if self._selected_index is None:
            messagebox.showinfo("提示", "请先选择要删除的按键")
            return
        if len(self.config.actions) <= 1:
            messagebox.showwarning("提示", "至少保留一条按键配置")
            return

        del self.config.actions[self._selected_index]
        self._selected_index = None
        self._refresh_action_list()

    def _save_current_action(self) -> None:
        if self._selected_index is None:
            messagebox.showinfo("提示", "请先选择要编辑的按键")
            return

        try:
            interval = int(self.interval_var.get().strip())
            cast_time = int(self.cast_var.get().strip())
            repeat = int(self.repeat_var.get().strip())
        except ValueError:
            messagebox.showerror("错误", "间隔、施法时间和次数必须是整数")
            return

        if interval < 10:
            messagebox.showerror("错误", "触发间隔不能小于 10 毫秒")
            return
        if cast_time < 0:
            messagebox.showerror("错误", "施法时间不能为负数")
            return
        if repeat < 0:
            messagebox.showerror("错误", "重复次数不能为负数")
            return

        key = self.key_var.get().strip().lower()
        if not key:
            messagebox.showerror("错误", "请填写按键")
            return

        action = self.config.actions[self._selected_index]
        action.enabled = self.enabled_var.get()
        action.key = key
        action.interval_ms = interval
        action.cast_time_ms = cast_time
        action.repeat_count = repeat
        self._refresh_action_list()
        self.tree.selection_set(str(self._selected_index))

    def _save_all(self) -> None:
        if self._selected_index is not None:
            self._save_current_action()
        self.config.toggle_hotkey = self.hotkey_var.get().strip().lower()
        save_config(self.config)
        messagebox.showinfo("成功", "配置已保存")

    def _reset_default(self) -> None:
        if messagebox.askyesno("确认", "确定恢复默认配置吗？"):
            self.engine.stop()
            self.config = AppConfig.default()
            self.hotkey_var.set(self.config.toggle_hotkey)
            self._selected_index = None
            self._refresh_action_list()
            self._register_hotkey()
            save_config(self.config)

    def _apply_hotkey(self) -> None:
        self.config.toggle_hotkey = self.hotkey_var.get().strip().lower()
        self._register_hotkey()
        self.toggle_btn.configure(text=f"开始 ({self.config.toggle_hotkey.upper()})")

    def _register_hotkey(self) -> None:
        self.hotkey_manager.register(self.config.toggle_hotkey, self._toggle_macro)

    def _toggle_macro(self) -> None:
        try:
            self.engine.toggle(self.config.actions)
        except ValueError as exc:
            messagebox.showwarning("提示", str(exc))

    def _on_engine_state_change(self, running: bool) -> None:
        def update() -> None:
            if running:
                self.status_var.set("状态：运行中")
                self.toggle_btn.configure(text=f"停止 ({self.config.toggle_hotkey.upper()})")
            else:
                self.status_var.set("状态：已停止")
                self.toggle_btn.configure(text=f"开始 ({self.config.toggle_hotkey.upper()})")

        self.root.after(0, update)

    def _on_close(self) -> None:
        self.engine.stop()
        self.hotkey_manager.unregister()
        if self._selected_index is not None:
            try:
                interval = int(self.interval_var.get().strip())
                cast_time = int(self.cast_var.get().strip())
                repeat = int(self.repeat_var.get().strip())
                key = self.key_var.get().strip().lower()
                if interval >= 10 and cast_time >= 0 and repeat >= 0 and key:
                    action = self.config.actions[self._selected_index]
                    action.enabled = self.enabled_var.get()
                    action.key = key
                    action.interval_ms = interval
                    action.cast_time_ms = cast_time
                    action.repeat_count = repeat
            except ValueError:
                pass
        self._save_all_silent()
        self.root.destroy()

    def _save_all_silent(self) -> None:
        self.config.toggle_hotkey = self.hotkey_var.get().strip().lower()
        save_config(self.config)


def main() -> None:
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except tk.TclError:
        pass
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    GameAssistantApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
