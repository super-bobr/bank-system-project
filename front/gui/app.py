"""Desktop GUI для банковской системы (tkinter).

Переиспользует всю бизнес-логику БЕЗ ИЗМЕНЕНИЙ: auth.py, session.py,
commands/*.py — те же функции, что и в CLI. Это просто другой "фронт".

Структура окна: три "экрана" (Frame), наложенные друг на друга —
LoginFrame, RegisterFrame, DashboardFrame. Показываем нужный через
tkraise(). Это стандартный паттерн переключения экранов в tkinter.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import auth
import session
from exceptions import BankError
from commands.balance import get_balance
from commands.deposit_withdraw import deposit, withdraw
from commands.transfer import transfer
from commands.history import last_transactions
from commands.profile import get_profile

TYPE_LABELS = {
    "deposit": "Пополнение",
    "withdraw": "Снятие",
    "transfer_in": "Перевод от",
    "transfer_out": "Перевод для",
}


class App(tk.Tk):
    """Главное окно: держит токен текущего пользователя и переключает экраны."""

    def __init__(self):
        super().__init__()
        self.title("Colony Bank")
        self.geometry("440x520")
        self.resizable(False, False)
        self.token = session.load_token()

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (LoginFrame, RegisterFrame, DashboardFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self._show_initial_frame()

    def _show_initial_frame(self):
        # Если есть сохранённый токен (файл ~/.bank_cli/session.json)
        # и он ещё валиден на сервере — сразу показываем дашборд.
        if self.token:
            try:
                auth.verify_token(self.token)
                self.show_frame(DashboardFrame)
                return
            except BankError:
                session.clear_token()
                self.token = None
        self.show_frame(LoginFrame)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.on_show()
        frame.tkraise()

    def set_token(self, token: str):
        self.token = token
        session.save_token(token)

    def logout(self):
        if self.token:
            try:
                auth.logout(self.token)
            except BankError:
                pass
        session.clear_token()
        self.token = None
        self.show_frame(LoginFrame)


class LoginFrame(ttk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Colony Bank", font=("Segoe UI", 20, "bold")).pack(pady=(30, 5))
        ttk.Label(self, text="Вход в аккаунт", font=("Segoe UI", 12)).pack(pady=(0, 20))

        form = ttk.Frame(self)
        form.pack()
        ttk.Label(form, text="Логин:").grid(row=0, column=0, sticky="w", pady=6)
        self.login_entry = ttk.Entry(form, width=28)
        self.login_entry.grid(row=0, column=1, pady=6)

        ttk.Label(form, text="Пароль:").grid(row=1, column=0, sticky="w", pady=6)
        self.password_entry = ttk.Entry(form, width=28, show="*")
        self.password_entry.grid(row=1, column=1, pady=6)
        self.password_entry.bind("<Return>", lambda e: self.do_login())

        ttk.Button(self, text="Войти", command=self.do_login).pack(pady=15)
        ttk.Button(
            self, text="Нет аккаунта? Регистрация",
            command=lambda: self.app.show_frame(RegisterFrame),
        ).pack()

        self.error_label = ttk.Label(self, text="", foreground="red", wraplength=380)
        self.error_label.pack(pady=15)

    def on_show(self):
        self.error_label.config(text="")
        self.password_entry.delete(0, "end")

    def do_login(self):
        login_value = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        try:
            token = auth.login(login_value, password)
            self.app.set_token(token)
            self.app.show_frame(DashboardFrame)
        except BankError as e:
            self.error_label.config(text=str(e))


class RegisterFrame(ttk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Регистрация", font=("Segoe UI", 18, "bold")).pack(pady=(30, 20))

        form = ttk.Frame(self)
        form.pack()

        ttk.Label(form, text="Имя:").grid(row=0, column=0, sticky="w", pady=6)
        self.name_entry = ttk.Entry(form, width=28)
        self.name_entry.grid(row=0, column=1, pady=6)

        ttk.Label(form, text="Логин:").grid(row=1, column=0, sticky="w", pady=6)
        self.username_entry = ttk.Entry(form, width=28)
        self.username_entry.grid(row=1, column=1, pady=6)

        ttk.Label(form, text="Пароль (от 6 симв.):").grid(row=2, column=0, sticky="w", pady=6)
        self.password_entry = ttk.Entry(form, width=28, show="*")
        self.password_entry.grid(row=2, column=1, pady=6)

        ttk.Button(self, text="Зарегистрироваться", command=self.do_register).pack(pady=15)
        ttk.Button(
            self, text="Уже есть аккаунт? Вход",
            command=lambda: self.app.show_frame(LoginFrame),
        ).pack()

        self.error_label = ttk.Label(self, text="", foreground="red", wraplength=380)
        self.error_label.pack(pady=15)

    def on_show(self):
        self.error_label.config(text="")
        for e in (self.name_entry, self.username_entry, self.password_entry):
            e.delete(0, "end")

    def do_register(self):
        try:
            # API друга сразу возвращает токен при регистрации (авто-вход) —
            # отдельно логиниться после этого не нужно.
            token = auth.register(
                self.name_entry.get().strip(),
                self.username_entry.get().strip(),
                self.password_entry.get().strip(),
            )
            self.app.set_token(token)
            self.app.show_frame(DashboardFrame)
        except BankError as e:
            self.error_label.config(text=str(e))


class DashboardFrame(ttk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app

        self.balance_label = ttk.Label(self, text="Баланс: —", font=("Segoe UI", 20, "bold"))
        self.balance_label.pack(pady=(20, 15))

        btns = ttk.Frame(self)
        btns.pack()
        ttk.Button(btns, text="⬆ Пополнить", width=18, command=self.do_deposit).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btns, text="⬇ Снять", width=18, command=self.do_withdraw).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btns, text="↔ Перевести", width=18, command=self.do_transfer).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(btns, text="👤 Профиль", width=18, command=self.do_profile).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(btns, text="🔄 Обновить", width=18, command=self.refresh).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(btns, text="🚪 Выйти", width=18, command=self.app.logout).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self, text="История последних операций:", font=("Segoe UI", 11, "bold")).pack(pady=(20, 5))
        self.history_text = tk.Text(self, width=50, height=11, state="disabled", wrap="word")
        self.history_text.pack(pady=5)

    def on_show(self):
        self.refresh()

    def refresh(self):
        try:
            bal = get_balance(self.app.token)
            self.balance_label.config(text=f"Баланс: {bal:.2f} ₽")
        except BankError as e:
            messagebox.showerror("Ошибка", str(e))
            return
        self._load_history()

    def _load_history(self):
        try:
            rows = last_transactions(self.app.token, limit=5)
        except BankError as e:
            messagebox.showerror("Ошибка", str(e))
            return
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", "end")
        if not rows:
            self.history_text.insert("end", "История операций пуста.")
        for r in rows:
            label = TYPE_LABELS.get(r["type"], r["type"])
            cp = f" ({r['counterparty_username']})" if r["counterparty_username"] else ""
            self.history_text.insert(
                "end",
                f"{r['created_at']:%Y-%m-%d %H:%M} — {label}{cp}: {r['amount']:.2f} ₽\n",
            )
        self.history_text.config(state="disabled")

    def do_deposit(self):
        amount = simpledialog.askstring("Пополнение", "Введите сумму пополнения:", parent=self)
        if amount is None:
            return
        try:
            new_balance = deposit(self.app.token, amount)
            messagebox.showinfo("Готово", f"Пополнено. Новый баланс: {new_balance:.2f} ₽")
        except BankError as e:
            messagebox.showerror("Ошибка", str(e))
        self.refresh()

    def do_withdraw(self):
        amount = simpledialog.askstring("Снятие", "Введите сумму снятия:", parent=self)
        if amount is None:
            return
        try:
            new_balance = withdraw(self.app.token, amount)
            messagebox.showinfo("Готово", f"Снято. Новый баланс: {new_balance:.2f} ₽")
        except BankError as e:
            messagebox.showerror("Ошибка", str(e))
        self.refresh()

    def do_transfer(self):
        target = simpledialog.askstring("Перевод", "Кому переводим (username)?", parent=self)
        if target is None:
            return
        amount = simpledialog.askstring("Перевод", "Введите сумму перевода:", parent=self)
        if amount is None:
            return
        try:
            result = transfer(self.app.token, target, amount)
            messagebox.showinfo(
                "Готово",
                f"Переведено {result['amount']:.2f} ₽ пользователю {result['target']}.\n"
                f"Ваш новый баланс: {result['new_balance']:.2f} ₽",
            )
        except BankError as e:
            messagebox.showerror("Ошибка", str(e))
        self.refresh()

    def do_profile(self):
        try:
            p = get_profile(self.app.token)
            messagebox.showinfo(
                "Профиль",
                f"Имя: {p['name']}\n"
                f"Логин: {p['username']}\n"
                f"Баланс: {p['balance']:.2f} {p['currency']}",
            )
        except BankError as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    app = App()
    app.mainloop()
