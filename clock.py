import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from datetime import datetime, date, timedelta

# ---------------------------------------------------------------------------
# Data file path (works both as script and as PyInstaller exe)
# ---------------------------------------------------------------------------
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(APP_DIR, "alarms.json")


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"daily_alarms": [], "one_time_alarms": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Notification popup
# ---------------------------------------------------------------------------
def show_notification(root, title_text, message, time_str):
    popup = tk.Toplevel(root)
    popup.title("通知")
    popup.attributes("-topmost", True)
    popup.resizable(False, False)

    # Center on screen
    popup.update_idletasks()
    w, h = 340, 200
    sw = popup.winfo_screenwidth()
    sh = popup.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    popup.geometry(f"{w}x{h}+{x}+{y}")
    popup.configure(bg="#FFFBE6")

    tk.Label(popup, text="🔔 通知", font=("Yu Gothic UI", 14, "bold"),
             bg="#FFFBE6", fg="#333").pack(pady=(18, 4))
    tk.Label(popup, text=message, font=("Yu Gothic UI", 12),
             bg="#FFFBE6", fg="#222", wraplength=300, justify="center").pack(pady=4)
    tk.Label(popup, text=time_str, font=("Yu Gothic UI", 10),
             bg="#FFFBE6", fg="#888").pack(pady=2)
    tk.Button(popup, text="  閉じる  ", font=("Yu Gothic UI", 11),
              command=popup.destroy, bg="#4A90D9", fg="white",
              relief="flat", padx=10, pady=4).pack(pady=18)

    popup.grab_set()


# ---------------------------------------------------------------------------
# Add/Edit dialogs
# ---------------------------------------------------------------------------
class DailyAlarmDialog(tk.Toplevel):
    def __init__(self, parent, alarm=None):
        super().__init__(parent)
        self.result = None
        self.title("毎日アラーム" + ("を編集" if alarm else "を追加"))
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(bg="#F5F5F5")
        self._build(alarm)
        self._center(parent)
        self.grab_set()
        self.wait_window()

    def _center(self, parent):
        self.update_idletasks()
        w, h = 320, 240
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self, alarm):
        pad = {"padx": 12, "pady": 6}
        frame = tk.Frame(self, bg="#F5F5F5")
        frame.pack(fill="both", expand=True, padx=16, pady=10)

        tk.Label(frame, text="時", bg="#F5F5F5").grid(row=0, column=0, sticky="w", **pad)
        self.hour_var = tk.StringVar(value=str(alarm["hour"]) if alarm else "8")
        tk.Spinbox(frame, textvariable=self.hour_var, from_=0, to=23,
                   width=5, format="%02.0f").grid(row=0, column=1, sticky="w", **pad)

        tk.Label(frame, text="分", bg="#F5F5F5").grid(row=1, column=0, sticky="w", **pad)
        self.minute_var = tk.StringVar(value=str(alarm["minute"]) if alarm else "0")
        tk.Spinbox(frame, textvariable=self.minute_var, from_=0, to=59,
                   width=5, format="%02.0f").grid(row=1, column=1, sticky="w", **pad)

        tk.Label(frame, text="メッセージ", bg="#F5F5F5").grid(row=2, column=0, sticky="w", **pad)
        self.msg_var = tk.StringVar(value=alarm["message"] if alarm else "")
        tk.Entry(frame, textvariable=self.msg_var, width=24).grid(row=2, column=1, sticky="ew", **pad)

        self.enabled_var = tk.BooleanVar(value=alarm.get("enabled", True) if alarm else True)
        tk.Checkbutton(frame, text="有効", variable=self.enabled_var,
                       bg="#F5F5F5").grid(row=3, column=0, columnspan=2, sticky="w", **pad)

        btn_frame = tk.Frame(self, bg="#F5F5F5")
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))
        tk.Button(btn_frame, text="登録", command=self._ok,
                  bg="#4A90D9", fg="white", relief="flat", padx=12, pady=4).pack(side="right", padx=4)
        tk.Button(btn_frame, text="キャンセル", command=self.destroy,
                  relief="flat", padx=12, pady=4).pack(side="right", padx=4)

    def _ok(self):
        try:
            h = int(self.hour_var.get())
            m = int(self.minute_var.get())
            assert 0 <= h <= 23 and 0 <= m <= 59
        except Exception:
            messagebox.showerror("入力エラー", "時・分を正しく入力してください", parent=self)
            return
        msg = self.msg_var.get().strip()
        if not msg:
            messagebox.showerror("入力エラー", "メッセージを入力してください", parent=self)
            return
        self.result = {"hour": h, "minute": m, "message": msg,
                       "enabled": self.enabled_var.get(), "last_triggered_date": None}
        self.destroy()


class OneTimeAlarmDialog(tk.Toplevel):
    def __init__(self, parent, alarm=None):
        super().__init__(parent)
        self.result = None
        self.title("単発アラーム" + ("を編集" if alarm else "を追加"))
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(bg="#F5F5F5")
        self._build(alarm)
        self._center(parent)
        self.grab_set()
        self.wait_window()

    def _center(self, parent):
        self.update_idletasks()
        w, h = 370, 340
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self, alarm):
        pad = {"padx": 12, "pady": 5}
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        # --- Tab 1: 直接指定 ---
        tab1 = tk.Frame(nb, bg="#F5F5F5")
        nb.add(tab1, text="直接入力")

        tk.Label(tab1, text="日付 (YYYY/MM/DD)", bg="#F5F5F5").grid(row=0, column=0, sticky="w", **pad)
        today = date.today().strftime("%Y/%m/%d")
        self.date_var = tk.StringVar(value=alarm["date"].replace("-", "/") if alarm else today)
        tk.Entry(tab1, textvariable=self.date_var, width=16).grid(row=0, column=1, sticky="w", **pad)

        tk.Label(tab1, text="時", bg="#F5F5F5").grid(row=1, column=0, sticky="w", **pad)
        self.hour_var = tk.StringVar(value=str(alarm["hour"]) if alarm else "9")
        tk.Spinbox(tab1, textvariable=self.hour_var, from_=0, to=23,
                   width=5, format="%02.0f").grid(row=1, column=1, sticky="w", **pad)

        tk.Label(tab1, text="分", bg="#F5F5F5").grid(row=2, column=0, sticky="w", **pad)
        self.minute_var = tk.StringVar(value=str(alarm["minute"]) if alarm else "0")
        tk.Spinbox(tab1, textvariable=self.minute_var, from_=0, to=59,
                   width=5, format="%02.0f").grid(row=2, column=1, sticky="w", **pad)

        tk.Label(tab1, text="メッセージ", bg="#F5F5F5").grid(row=3, column=0, sticky="w", **pad)
        self.msg_var = tk.StringVar(value=alarm["message"] if alarm else "")
        tk.Entry(tab1, textvariable=self.msg_var, width=24).grid(row=3, column=1, sticky="ew", **pad)

        self.enabled_var = tk.BooleanVar(value=alarm.get("enabled", True) if alarm else True)
        tk.Checkbutton(tab1, text="有効", variable=self.enabled_var,
                       bg="#F5F5F5").grid(row=4, column=0, columnspan=2, sticky="w", **pad)

        # --- Tab 2: 予定時刻から逆算 ---
        tab2 = tk.Frame(nb, bg="#F5F5F5")
        nb.add(tab2, text="○分前に通知")

        tk.Label(tab2, text="予定日 (YYYY/MM/DD)", bg="#F5F5F5").grid(row=0, column=0, sticky="w", **pad)
        self.before_date_var = tk.StringVar(value=today)
        tk.Entry(tab2, textvariable=self.before_date_var, width=16).grid(row=0, column=1, sticky="w", **pad)

        tk.Label(tab2, text="予定時刻 (時)", bg="#F5F5F5").grid(row=1, column=0, sticky="w", **pad)
        self.before_hour_var = tk.StringVar(value="15")
        tk.Spinbox(tab2, textvariable=self.before_hour_var, from_=0, to=23,
                   width=5, format="%02.0f").grid(row=1, column=1, sticky="w", **pad)

        tk.Label(tab2, text="予定時刻 (分)", bg="#F5F5F5").grid(row=2, column=0, sticky="w", **pad)
        self.before_minute_var = tk.StringVar(value="0")
        tk.Spinbox(tab2, textvariable=self.before_minute_var, from_=0, to=59,
                   width=5, format="%02.0f").grid(row=2, column=1, sticky="w", **pad)

        tk.Label(tab2, text="何分前", bg="#F5F5F5").grid(row=3, column=0, sticky="w", **pad)
        self.before_min_var = tk.StringVar(value="10")
        tk.Spinbox(tab2, textvariable=self.before_min_var, from_=1, to=120,
                   width=5).grid(row=3, column=1, sticky="w", **pad)

        tk.Label(tab2, text="メモ (省略可)", bg="#F5F5F5").grid(row=4, column=0, sticky="w", **pad)
        self.before_label_var = tk.StringVar(value="")
        tk.Entry(tab2, textvariable=self.before_label_var, width=24).grid(row=4, column=1, sticky="ew", **pad)

        self.nb = nb

        btn_frame = tk.Frame(self, bg="#F5F5F5")
        btn_frame.pack(fill="x", padx=12, pady=(0, 12))
        tk.Button(btn_frame, text="登録", command=self._ok,
                  bg="#4A90D9", fg="white", relief="flat", padx=12, pady=4).pack(side="right", padx=4)
        tk.Button(btn_frame, text="キャンセル", command=self.destroy,
                  relief="flat", padx=12, pady=4).pack(side="right", padx=4)

    def _ok(self):
        tab = self.nb.index(self.nb.select())

        if tab == 0:
            # 直接指定
            date_str = self.date_var.get().strip()
            try:
                d = datetime.strptime(date_str, "%Y/%m/%d").date()
            except Exception:
                messagebox.showerror("入力エラー", "日付を YYYY/MM/DD 形式で入力してください", parent=self)
                return
            try:
                h = int(self.hour_var.get())
                m = int(self.minute_var.get())
                assert 0 <= h <= 23 and 0 <= m <= 59
            except Exception:
                messagebox.showerror("入力エラー", "時・分を正しく入力してください", parent=self)
                return
            msg = self.msg_var.get().strip()
            if not msg:
                messagebox.showerror("入力エラー", "メッセージを入力してください", parent=self)
                return
            self.result = {
                "date": d.strftime("%Y-%m-%d"),
                "hour": h, "minute": m,
                "message": msg,
                "enabled": self.enabled_var.get(),
                "done": False,
            }
        else:
            # 逆算
            date_str = self.before_date_var.get().strip()
            try:
                d = datetime.strptime(date_str, "%Y/%m/%d").date()
            except Exception:
                messagebox.showerror("入力エラー", "予定日を YYYY/MM/DD 形式で入力してください", parent=self)
                return
            try:
                ph = int(self.before_hour_var.get())
                pm = int(self.before_minute_var.get())
                before = int(self.before_min_var.get())
                assert 0 <= ph <= 23 and 0 <= pm <= 59 and before >= 1
            except Exception:
                messagebox.showerror("入力エラー", "時・分・分前を正しく入力してください", parent=self)
                return
            planned = datetime.combine(d, __import__("datetime").time(ph, pm))
            notify = planned - timedelta(minutes=before)
            label = self.before_label_var.get().strip()
            event_name = label if label else f"{ph:02d}:{pm:02d}の予定"
            msg = f"{ph:02d}:{pm:02d} {event_name}の{before}分前です"
            self.result = {
                "date": notify.date().strftime("%Y-%m-%d"),
                "hour": notify.hour, "minute": notify.minute,
                "message": msg,
                "enabled": True,
                "done": False,
            }
        self.destroy()


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------
class AlarmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("静かなアラーム時計")
        self.root.minsize(640, 480)
        self.root.configure(bg="#FAFAFA")
        self.data = load_data()
        self._build_ui()
        self._refresh_lists()
        self._tick()

    # -----------------------------------------------------------------------
    # UI construction
    # -----------------------------------------------------------------------
    def _build_ui(self):
        # Top: current time
        top = tk.Frame(self.root, bg="#2C3E50")
        top.pack(fill="x")
        self.clock_label = tk.Label(top, text="", font=("Yu Gothic UI", 22, "bold"),
                                    bg="#2C3E50", fg="#ECF0F1", pady=10)
        self.clock_label.pack()

        # Notebook: two tabs
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=10, pady=8)

        # --- Daily tab ---
        daily_frame = tk.Frame(nb, bg="#FAFAFA")
        nb.add(daily_frame, text="  毎日アラーム  ")
        self._build_list_frame(daily_frame, "daily")

        # --- One-time tab ---
        onetime_frame = tk.Frame(nb, bg="#FAFAFA")
        nb.add(onetime_frame, text="  単発アラーム  ")
        self._build_list_frame(onetime_frame, "onetime")

        self.nb = nb

    def _build_list_frame(self, parent, kind):
        columns = (
            ("状態", 60), ("時刻", 70), ("メッセージ", 300),
        ) if kind == "daily" else (
            ("状態", 60), ("日付", 90), ("時刻", 70), ("メッセージ", 260),
        )

        col_ids = [c[0] for c in columns]
        tree = ttk.Treeview(parent, columns=col_ids, show="headings", selectmode="browse")
        for name, width in columns:
            tree.heading(name, text=name)
            tree.column(name, width=width, anchor="center" if name in ("状態", "時刻", "日付") else "w")

        vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        vsb.pack(side="left", fill="y", pady=8)

        btn_frame = tk.Frame(parent, bg="#FAFAFA")
        btn_frame.pack(side="right", fill="y", padx=8, pady=8)

        style = {"relief": "flat", "padx": 10, "pady": 6, "width": 8,
                 "font": ("Yu Gothic UI", 10)}
        tk.Button(btn_frame, text="追加", bg="#4A90D9", fg="white",
                  command=lambda: self._add(kind), **style).pack(pady=3)
        tk.Button(btn_frame, text="編集", bg="#7FB77E", fg="white",
                  command=lambda: self._edit(kind, tree), **style).pack(pady=3)
        tk.Button(btn_frame, text="削除", bg="#E74C3C", fg="white",
                  command=lambda: self._delete(kind, tree), **style).pack(pady=3)
        tk.Button(btn_frame, text="有効化", bg="#F39C12", fg="white",
                  command=lambda: self._toggle(kind, tree, True), **style).pack(pady=3)
        tk.Button(btn_frame, text="無効化", bg="#95A5A6", fg="white",
                  command=lambda: self._toggle(kind, tree, False), **style).pack(pady=3)

        if kind == "daily":
            self.daily_tree = tree
        else:
            self.onetime_tree = tree

    # -----------------------------------------------------------------------
    # List refresh
    # -----------------------------------------------------------------------
    def _refresh_lists(self):
        # Daily
        for row in self.daily_tree.get_children():
            self.daily_tree.delete(row)
        for i, a in enumerate(self.data["daily_alarms"]):
            status = "有効" if a["enabled"] else "無効"
            time_str = f"{a['hour']:02d}:{a['minute']:02d}"
            self.daily_tree.insert("", "end", iid=str(i),
                                   values=(status, time_str, a["message"]))

        # One-time
        for row in self.onetime_tree.get_children():
            self.onetime_tree.delete(row)
        for i, a in enumerate(self.data["one_time_alarms"]):
            if a.get("done"):
                status = "完了"
            elif a["enabled"]:
                status = "有効"
            else:
                status = "無効"
            time_str = f"{a['hour']:02d}:{a['minute']:02d}"
            self.onetime_tree.insert("", "end", iid=str(i),
                                     values=(status, a["date"], time_str, a["message"]))

    # -----------------------------------------------------------------------
    # Alarm checking (runs via root.after — no threading needed)
    # -----------------------------------------------------------------------
    def _tick(self):
        now = datetime.now()
        self.clock_label.config(text=now.strftime("%Y/%m/%d  %H:%M:%S"))
        self._check_alarms(now)
        self.root.after(1000, self._tick)

    def _check_alarms(self, now):
        changed = False
        today_str = date.today().strftime("%Y-%m-%d")

        for a in self.data["daily_alarms"]:
            if not a["enabled"]:
                continue
            if a.get("last_triggered_date") == today_str:
                continue
            if now.hour == a["hour"] and now.minute == a["minute"]:
                a["last_triggered_date"] = today_str
                changed = True
                show_notification(self.root, "通知", a["message"],
                                  f"{a['hour']:02d}:{a['minute']:02d}")

        for a in self.data["one_time_alarms"]:
            if not a["enabled"] or a.get("done"):
                continue
            if (a["date"] == today_str and
                    now.hour == a["hour"] and now.minute == a["minute"]):
                a["done"] = True
                changed = True
                show_notification(self.root, "通知", a["message"],
                                  f"{a['hour']:02d}:{a['minute']:02d}")

        if changed:
            save_data(self.data)
            self._refresh_lists()

    # -----------------------------------------------------------------------
    # CRUD
    # -----------------------------------------------------------------------
    def _add(self, kind):
        if kind == "daily":
            dlg = DailyAlarmDialog(self.root)
            if dlg.result:
                self.data["daily_alarms"].append(dlg.result)
                save_data(self.data)
                self._refresh_lists()
        else:
            dlg = OneTimeAlarmDialog(self.root)
            if dlg.result:
                self.data["one_time_alarms"].append(dlg.result)
                save_data(self.data)
                self._refresh_lists()

    def _selected_index(self, tree):
        sel = tree.selection()
        if not sel:
            return None
        return int(sel[0])

    def _edit(self, kind, tree):
        idx = self._selected_index(tree)
        if idx is None:
            messagebox.showinfo("選択してください", "編集するアラームを選択してください")
            return
        if kind == "daily":
            alarm = self.data["daily_alarms"][idx]
            dlg = DailyAlarmDialog(self.root, alarm=alarm)
            if dlg.result:
                dlg.result["last_triggered_date"] = alarm.get("last_triggered_date")
                self.data["daily_alarms"][idx] = dlg.result
                save_data(self.data)
                self._refresh_lists()
        else:
            alarm = self.data["one_time_alarms"][idx]
            dlg = OneTimeAlarmDialog(self.root, alarm=alarm)
            if dlg.result:
                dlg.result["done"] = alarm.get("done", False)
                self.data["one_time_alarms"][idx] = dlg.result
                save_data(self.data)
                self._refresh_lists()

    def _delete(self, kind, tree):
        idx = self._selected_index(tree)
        if idx is None:
            messagebox.showinfo("選択してください", "削除するアラームを選択してください")
            return
        if not messagebox.askyesno("確認", "このアラームを削除しますか？"):
            return
        if kind == "daily":
            self.data["daily_alarms"].pop(idx)
        else:
            self.data["one_time_alarms"].pop(idx)
        save_data(self.data)
        self._refresh_lists()

    def _toggle(self, kind, tree, enabled):
        idx = self._selected_index(tree)
        if idx is None:
            messagebox.showinfo("選択してください", "アラームを選択してください")
            return
        if kind == "daily":
            self.data["daily_alarms"][idx]["enabled"] = enabled
        else:
            self.data["one_time_alarms"][idx]["enabled"] = enabled
        save_data(self.data)
        self._refresh_lists()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    root = tk.Tk()
    app = AlarmApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
