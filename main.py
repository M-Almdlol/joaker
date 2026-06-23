import flet as ft
import sqlite3
import datetime


def init_db():
    conn = sqlite3.connect('game_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS game_data (
                      team1 TEXT, team2 TEXT,
                      G1_T1 TEXT, G1_T2 TEXT, G1_T3 TEXT, G1_T4 TEXT, G1_T5 TEXT,
                      G2_T1 TEXT, G2_T2 TEXT, G2_T3 TEXT, G2_T4 TEXT, G2_T5 TEXT,
                      G1_T TEXT, G2_T TEXT,
                      total_team TEXT, team_win TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS match_history (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      team1_name TEXT, team2_name TEXT,
                      team1_score INTEGER, team2_score INTEGER,
                      winner TEXT, date TEXT)''')
    conn.commit()
    conn.close()

def main(page: ft.Page):
    init_db()
    
    page.title = "جواكر - لوحة النتائج"
    page.scroll = "auto"
    page.bgcolor = "#f4f6f8"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 500
    page.window_height = 800
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # حقول أسماء الفرق
    team1_name = ft.TextField(label="الفريق الأول", value="", text_align=ft.TextAlign.CENTER, rtl=True, expand=True, border_color=ft.Colors.BLUE, color=ft.Colors.BLUE, border_radius=10, dense=True, content_padding=10, text_style=ft.TextStyle(weight=ft.FontWeight.BOLD))
    team2_name = ft.TextField(label="الفريق الثاني", value="", text_align=ft.TextAlign.CENTER, rtl=True, expand=True, border_color=ft.Colors.RED, color=ft.Colors.RED, border_radius=10, dense=True, content_padding=10, text_style=ft.TextStyle(weight=ft.FontWeight.BOLD))

    # فلتر إدخال الأرقام وعلامة السالب فقط
    rounds_filter = ft.InputFilter(allow=True, regex_string=r"^-?[0-9]*", replacement_string="")

    # جولات الفريقين
    t1_rounds = [ft.TextField(label=f"الجولة {i+1}", value="", text_align=ft.TextAlign.CENTER, rtl=True, keyboard_type=ft.KeyboardType.NUMBER, input_filter=rounds_filter, border_radius=10, dense=True, content_padding=10) for i in range(5)]
    t2_rounds = [ft.TextField(label=f"الجولة {i+1}", value="", text_align=ft.TextAlign.CENTER, rtl=True, keyboard_type=ft.KeyboardType.NUMBER, input_filter=rounds_filter, border_radius=10, dense=True, content_padding=10) for i in range(5)]

    # مجاميع الفرق
    t1_total = ft.TextField(label="المجموع", value="0", text_align=ft.TextAlign.CENTER, rtl=True, read_only=True, border_color=ft.Colors.GREEN, border_radius=10, dense=True, content_padding=10, text_style=ft.TextStyle(weight=ft.FontWeight.BOLD))
    t2_total = ft.TextField(label="المجموع", value="0", text_align=ft.TextAlign.CENTER, rtl=True, read_only=True, border_color=ft.Colors.GREEN, border_radius=10, dense=True, content_padding=10, text_style=ft.TextStyle(weight=ft.FontWeight.BOLD))

    # حقول إضافية للفارق والفائز
    diff_field = ft.TextField(label="فارق النقاط", value="0", text_align=ft.TextAlign.CENTER, rtl=True, read_only=True, border_radius=10, expand=True, dense=True, content_padding=10, text_style=ft.TextStyle(weight=ft.FontWeight.BOLD))
    winner_field = ft.TextField(label="الفريق المنتصر", value="لا يوجد فائز", text_align=ft.TextAlign.CENTER, rtl=True, read_only=True, border_radius=10, expand=True, dense=True, content_padding=10, text_style=ft.TextStyle(weight=ft.FontWeight.BOLD))

    def save_state():
        conn = sqlite3.connect('game_data.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM game_data')
        
        t1_vals = [f.value for f in t1_rounds]
        t2_vals = [f.value for f in t2_rounds]
        
        cursor.execute('''INSERT INTO game_data 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (team1_name.value, team2_name.value, 
                        *t1_vals, *t2_vals,
                        t1_total.value, t2_total.value, diff_field.value, winner_field.value))
        conn.commit()
        conn.close()

    def update_scores(e=None):
        def calc_total(fields):
            total = 0
            for f in fields:
                val = (f.value or "").strip()
                if val:
                    try:
                        total += int(float(val))
                        f.bgcolor = ft.Colors.YELLOW_100
                    except ValueError:
                        f.bgcolor = ft.Colors.RED_100
                else:
                    f.bgcolor = None
                f.update()
            return total

        t1_sum = calc_total(t1_rounds)
        t2_sum = calc_total(t2_rounds)
        
        t1_total.value = str(t1_sum)
        t2_total.value = str(t2_sum)
        t1_total.update()
        t2_total.update()

        diff = abs(t1_sum - t2_sum)
        diff_field.value = str(diff)
        diff_field.update()

        n1 = (team1_name.value or "").strip() or "الفريق الأول"
        n2 = (team2_name.value or "").strip() or "الفريق الثاني"

        if t1_sum < t2_sum:
            winner_field.value = n1
            winner_field.color = team1_name.color
            winner_field.border_color = team1_name.border_color
            diff_field.color = team1_name.color
            diff_field.border_color = team1_name.border_color
        elif t2_sum < t1_sum:
            winner_field.value = n2
            winner_field.color = team2_name.color
            winner_field.border_color = team2_name.border_color
            diff_field.color = team2_name.color
            diff_field.border_color = team2_name.border_color
        else:
            winner_field.value = "تعادل"
            winner_field.color = ft.Colors.BLACK
            winner_field.border_color = None
            diff_field.color = ft.Colors.BLACK
            diff_field.border_color = None
            
        winner_field.update()
        diff_field.update()
        save_state()

    # ربط الأحداث
    team1_name.on_change = update_scores
    team2_name.on_change = update_scores
    for f in t1_rounds + t2_rounds:
        f.on_change = update_scores

    def load_state():
        conn = sqlite3.connect('game_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM game_data')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            team1_name.value = row[0] if row[0] is not None else ""
            team2_name.value = row[1] if row[1] is not None else ""
            for i, f in enumerate(t1_rounds):
                f.value = row[2+i] if row[2+i] is not None else ""
            for i, f in enumerate(t2_rounds):
                f.value = row[7+i] if row[7+i] is not None else ""
            t1_total.value = row[12] if row[12] is not None else "0"
            t2_total.value = row[13] if row[13] is not None else "0"
            diff_field.value = row[14] if row[14] is not None else "0"
            winner_field.value = row[15] if row[15] is not None else "لا يوجد فائز"
        
        update_scores()

    def reset_board(e=None):
        team1_name.value = ""
        team2_name.value = ""
        for f in t1_rounds + t2_rounds:
            f.value = ""
        update_scores()

    def end_game(e):
        if t1_total.value == "0" and t2_total.value == "0":
            return # لا يوجد ما يتم حفظه
            
        n1 = (team1_name.value or "").strip() or "الفريق الأول"
        n2 = (team2_name.value or "").strip() or "الفريق الثاني"
        
        conn = sqlite3.connect('game_data.db')
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute('''INSERT INTO match_history (team1_name, team2_name, team1_score, team2_score, winner, date)
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                       (n1, n2, int(t1_total.value), int(t2_total.value), winner_field.value, now))
        conn.commit()
        conn.close()
        
        # إظهار رسالة تأكيد
        page.snack_bar = ft.SnackBar(ft.Text("تم حفظ النتيجة بنجاح في سجل المباريات", rtl=True), bgcolor=ft.Colors.GREEN)
        page.snack_bar.open = True
        page.update()
        reset_board()

    # نافذة سجل المباريات — تُنشأ مرة واحدة فقط وتبقى في overlay
    history_list = ft.ListView(expand=True, spacing=10)
    history_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("سجل المباريات", rtl=True, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
        content=ft.Container(history_list, width=400, height=400),
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=15),
        on_dismiss=lambda e: None,
    )
    history_dlg.actions = [ft.TextButton("إغلاق", on_click=lambda _: close_dlg())]
    page.overlay.append(history_dlg)

    def show_history(e):
        conn = sqlite3.connect('game_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT team1_name, team2_name, team1_score, team2_score, winner, date FROM match_history ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()

        # تحديث محتوى القائمة في كل مرة
        history_list.controls.clear()
        if not rows:
            history_list.controls.append(
                ft.Text("لا توجد مباريات مسجلة بعد.", text_align=ft.TextAlign.CENTER, rtl=True)
            )
        else:
            for row in rows:
                t1, t2, s1, s2, win, match_date = row
                history_list.controls.append(
                    ft.Card(
                        elevation=3,
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(match_date, size=12, color=ft.Colors.GREY_600),
                                ft.Row([
                                    ft.Text(f"{t1}: {s1}", weight=ft.FontWeight.BOLD, size=16),
                                    ft.Text("ضد", color=ft.Colors.BLUE_GREY),
                                    ft.Text(f"{t2}: {s2}", weight=ft.FontWeight.BOLD, size=16),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, rtl=True),
                                ft.Text(f"الفائز: {win}", color=ft.Colors.GREEN_700, weight=ft.FontWeight.W_600)
                            ], rtl=True),
                            padding=15
                        )
                    )
                )

        history_dlg.open = True
        page.update()

    def close_dlg():
        history_dlg.open = False
        page.update()

    # Layout Elements
    app_bar = ft.AppBar(
        title=ft.Text("لوحة نتائج جواكر", weight=ft.FontWeight.BOLD, color="white"),
        bgcolor="#e3113e",
        center_title=True,
        actions=[
            ft.IconButton(ft.Icons.HISTORY, on_click=show_history, tooltip="سجل المباريات", icon_color="white"),
            ft.IconButton(ft.Icons.AUTORENEW, on_click=reset_board, tooltip="تصفير اللوحة", icon_color="white")
        ]
    )
    
    page.appbar = app_bar

    # البطاقة الرئيسية (اللوحة)
    main_card = ft.Card(
        elevation=8,
        shape=ft.RoundedRectangleBorder(radius=20),
        content=ft.Container(
            padding=15,
            content=ft.Column([
                # أسماء الفرق
                ft.Row([team1_name, team2_name], alignment=ft.MainAxisAlignment.CENTER, rtl=True),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                
                # إدخال الجولات والمجاميع
                ft.Row([
                    ft.Column(t1_rounds + [ft.Divider(height=10), t1_total], expand=True, alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                    ft.Container(width=1, bgcolor=ft.Colors.GREY_300, height=280, margin=ft.margin.symmetric(horizontal=5)), # فاصل رأسي
                    ft.Column(t2_rounds + [ft.Divider(height=10), t2_total], expand=True, alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                ], alignment=ft.MainAxisAlignment.CENTER, rtl=True),
                
                ft.Divider(height=20, color=ft.Colors.GREY_300),
                
                # الفائز والفارق
                ft.Row([winner_field, diff_field], alignment=ft.MainAxisAlignment.CENTER, rtl=True),
                ft.Container(height=5),
                
                # زر إنهاء وحفظ اللعبة
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SAVE),
                        ft.Text("إنهاء المباراة وحفظ النتيجة", weight=ft.FontWeight.BOLD, size=16),
                    ], alignment=ft.MainAxisAlignment.CENTER, rtl=True),
                    on_click=end_game,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREEN_600,
                        color="white",
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=10
                    ),
                )
            ], rtl=True, spacing=5)
        )
    )

    page.add(
        ft.Container(
            content=main_card,
            padding=ft.padding.symmetric(vertical=20, horizontal=10),
            alignment=ft.alignment.center
        )
    )
    
    load_state()

if __name__ == '__main__':
    ft.app(target=main)
