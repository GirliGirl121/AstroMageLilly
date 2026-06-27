#!/usr/bin/env python3
"""
MagiJournal — Desktop GUI Application
A modern dark-themed astrological calendar, diary, and journal.

Author: Lilly for Gigi ❤️
Date: 2026-06-24
"""

import sys
import os
import json
import subprocess
from datetime import datetime, date, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QStackedWidget, QListWidget,
    QListWidgetItem, QTextEdit, QLineEdit, QCheckBox, QComboBox,
    QCalendarWidget, QScrollArea, QFrame, QSplitter, QTabWidget,
    QToolBar, QStatusBar, QMessageBox, QInputDialog, QMenu,
    QGroupBox, QFormLayout, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal, QSize, QUrl
from PyQt6.QtGui import QFont, QIcon, QColor, QAction, QPalette, QDesktopServices
from PyQt6.QtWidgets import QSystemTrayIcon

from database import get_database
from calendar_engine import get_day_data, get_month_data, get_week_data, PICATRIX_SPIRITS, CHALEDEAN_AR
from simply_astrology_view import SimplyAstrologyView

# ─── Dark Theme Stylesheet ───────────────────────────────────────────────────
STYLESHEET = """
QMainWindow {
    background-color: #0d0d1a;
}
QWidget {
    background-color: #0d0d1a;
    color: #e0e0e0;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}
QFrame#card {
    background-color: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 10px;
    padding: 12px;
}
QFrame#dayCard {
    background-color: #12122a;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 6px;
    margin: 2px;
}
QFrame#dayCard:hover {
    border: 1px solid #d4a843;
    background-color: #1a1a3a;
}
QFrame#dayCardSelected {
    background-color: #1a1a3e;
    border: 2px solid #d4a843;
    border-radius: 8px;
    padding: 6px;
    margin: 2px;
}
QPushButton {
    background-color: #2a2a4a;
    color: #e0e0e0;
    border: 1px solid #3a3a5a;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #3a3a5a;
    border: 1px solid #d4a843;
}
QPushButton:pressed {
    background-color: #d4a843;
    color: #0d0d1a;
}
QPushButton#primaryBtn {
    background-color: #d4a843;
    color: #0d0d1a;
    font-weight: bold;
    border: none;
}
QPushButton#primaryBtn:hover {
    background-color: #e8c060;
}
QPushButton#navBtn {
    background-color: transparent;
    border: none;
    color: #888;
    padding: 8px 12px;
    text-align: left;
    font-size: 13px;
}
QPushButton#navBtn:hover {
    color: #d4a843;
    background-color: #1a1a2e;
}
QPushButton#navBtnActive {
    background-color: #1a1a2e;
    color: #d4a843;
    border-left: 3px solid #d4a843;
    font-weight: bold;
}
QPushButton#smallBtn {
    padding: 4px 8px;
    font-size: 11px;
    border-radius: 4px;
}
QListWidget {
    background-color: #12122a;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 4px;
}
QListWidget::item {
    padding: 6px;
    border-radius: 4px;
}
QListWidget::item:hover {
    background-color: #1a1a3a;
}
QListWidget::item:selected {
    background-color: #2a2a4a;
    color: #d4a843;
}
QTextEdit, QLineEdit {
    background-color: #12122a;
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    padding: 8px;
    color: #e0e0e0;
    font-size: 13px;
}
QTextEdit:focus, QLineEdit:focus {
    border: 1px solid #d4a843;
}
QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #3a3a5a;
    background-color: #12122a;
}
QCheckBox::indicator:checked {
    background-color: #d4a843;
    border: 2px solid #d4a843;
}
QComboBox {
    background-color: #12122a;
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    padding: 6px;
    color: #e0e0e0;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #1a1a2e;
    border: 1px solid #2a2a4a;
    selection-background-color: #2a2a4a;
}
QScrollBar:vertical {
    background-color: #0d0d1a;
    width: 10px;
}
QScrollBar::handle:vertical {
    background-color: #3a3a5a;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #d4a843;
}
QTabWidget::pane {
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    background-color: #1a1a2e;
}
QTabBar::tab {
    background-color: #12122a;
    color: #888;
    padding: 8px 16px;
    border: 1px solid #2a2a4a;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #1a1a2e;
    color: #d4a843;
    font-weight: bold;
}
QLabel#title {
    font-size: 24px;
    font-weight: bold;
    color: #d4a843;
}
QLabel#subtitle {
    font-size: 14px;
    color: #888;
}
QLabel#section {
    font-size: 16px;
    font-weight: bold;
    color: #c77dff;
    margin-top: 12px;
    margin-bottom: 6px;
}
QLabel#small {
    font-size: 11px;
    color: #888;
}
QLabel#planet {
    font-size: 14px;
    font-weight: bold;
    color: #7ec8e3;
}
QLabel#mansion {
    font-size: 13px;
    color: #c77dff;
}
QLabel#dayNum {
    font-size: 16px;
    font-weight: bold;
    color: #e0e0e0;
}
QLabel#dayNumSmall {
    font-size: 12px;
    color: #888;
}
QSplitter::handle {
    background-color: #2a2a4a;
}
QSplitter::handle:horizontal {
    width: 2px;
}
QSplitter::handle:vertical {
    height: 2px;
}
QStatusBar {
    background-color: #12122a;
    color: #888;
    border-top: 1px solid #2a2a4a;
}
QToolBar {
    background-color: #12122a;
    border-bottom: 1px solid #2a2a4a;
    spacing: 4px;
    padding: 4px;
}
"""


# ─── Helper Functions ─────────────────────────────────────────────────────────
def get_planet_symbol(planet):
    symbols = {'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂', 'Jupiter': '♃', 'Saturn': '♄'}
    return symbols.get(planet, '')

def get_mansion_symbol(index):
    symbols = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓']
    return symbols[index % 12]


# ─── Month View ───────────────────────────────────────────────────────────────
class MonthView(QWidget):
    day_selected = pyqtSignal(date)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.year = datetime.now().year
        self.month = datetime.now().month
        self.selected_date = None
        self.day_data_cache = {}
        self.init_ui()
        self.load_month_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        header.addWidget(self.title_label)
        
        header.addStretch()
        
        prev_btn = QPushButton("◀ Prev")
        prev_btn.setObjectName("smallBtn")
        prev_btn.clicked.connect(self.prev_month)
        header.addWidget(prev_btn)
        
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(y) for y in range(2020, 2031)])
        self.year_combo.setCurrentText(str(self.year))
        self.year_combo.currentTextChanged.connect(self.change_year)
        header.addWidget(self.year_combo)
        
        next_btn = QPushButton("Next ▶")
        next_btn.setObjectName("smallBtn")
        next_btn.clicked.connect(self.next_month)
        header.addWidget(next_btn)
        
        layout.addLayout(header)
        
        # Day headers
        days_header = QHBoxLayout()
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            lbl = QLabel(day)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setObjectName("small")
            lbl.setFixedHeight(24)
            days_header.addWidget(lbl)
        layout.addLayout(days_header)
        
        # Calendar grid
        self.grid = QGridLayout()
        self.grid.setSpacing(2)
        layout.addLayout(self.grid)
        layout.addStretch()
    
    def load_month_data(self):
        self.day_data_cache = {}
        data = get_month_data(self.year, self.month)
        for day_data in data:
            d = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
            self.day_data_cache[d.day] = day_data
        
        self.title_label.setText(f"{datetime(self.year, self.month, 1).strftime('%B %Y')}")
        self.populate_grid()
    
    def populate_grid(self):
        # Clear existing
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        cal = []
        first_day = date(self.year, self.month, 1)
        # Monday=0 in Python
        start_weekday = first_day.weekday()
        
        # Build 6-week grid
        day = 1
        days_in_month = (date(self.year, self.month + 1, 1) - timedelta(days=1)).day if self.month < 12 else 31
        
        for week in range(6):
            cal_week = []
            for weekday in range(7):
                if week == 0 and weekday < start_weekday:
                    cal_week.append(None)
                elif day > days_in_month:
                    cal_week.append(None)
                else:
                    cal_week.append(day)
                    day += 1
            cal.append(cal_week)
        
        for week_idx, week in enumerate(cal):
            for weekday_idx, day_num in enumerate(week):
                if day_num is None:
                    empty = QWidget()
                    empty.setFixedSize(100, 70)
                    self.grid.addWidget(empty, week_idx, weekday_idx)
                else:
                    day_data = self.day_data_cache.get(day_num)
                    card = self.create_day_card(day_num, day_data)
                    self.grid.addWidget(card, week_idx, weekday_idx)
    
    def create_day_card(self, day_num, day_data):
        card = QFrame()
        card.setObjectName("dayCard")
        card.setFixedSize(100, 70)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if day_data and self.selected_date == date(self.year, self.month, day_num):
            card.setObjectName("dayCardSelected")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # Day number
        day_lbl = QLabel(str(day_num))
        day_lbl.setObjectName("dayNumSmall")
        layout.addWidget(day_lbl)
        
        if day_data:
            # Moon sign
            moon_lbl = QLabel(f"☽ {day_data['moon_sign'][:3]}")
            moon_lbl.setObjectName("small")
            layout.addWidget(moon_lbl)
            
            # Mansion
            mansion = day_data.get('moon_mansion', '')
            if mansion:
                m_lbl = QLabel(f"{mansion[:8]}")
                m_lbl.setObjectName("mansion")
                m_lbl.setFont(QFont("", 9))
                layout.addWidget(m_lbl)
            
            # Day ruler
            ruler = day_data.get('day_ruler', '')
            if ruler:
                r_lbl = QLabel(f"{get_planet_symbol(ruler)} {ruler[:3]}")
                r_lbl.setObjectName("small")
                r_lbl.setStyleSheet("color: #d4a843;")
                layout.addWidget(r_lbl)
        
        # Click handler
        card.mousePressEvent = lambda e, d=date(self.year, self.month, day_num): self.on_day_clicked(d)
        
        return card
    
    def on_day_clicked(self, d):
        self.selected_date = d
        self.populate_grid()
        self.day_selected.emit(d)
    
    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.load_month_data()
    
    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.load_month_data()
    
    def change_year(self, year_str):
        self.year = int(year_str)
        self.load_month_data()


# ─── Daily Diary Page ─────────────────────────────────────────────────────────
class DailyDiaryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = datetime.now().date()
        self.db = get_database()
        self.init_ui()
        self.load_day()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header with date navigation
        header = QHBoxLayout()
        prev_btn = QPushButton("◀")
        prev_btn.setObjectName("smallBtn")
        prev_btn.setFixedSize(36, 36)
        prev_btn.clicked.connect(self.prev_day)
        header.addWidget(prev_btn)
        
        self.date_label = QLabel()
        self.date_label.setObjectName("title")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(self.date_label)
        
        next_btn = QPushButton("▶")
        next_btn.setObjectName("smallBtn")
        next_btn.setFixedSize(36, 36)
        next_btn.clicked.connect(self.next_day)
        header.addWidget(next_btn)
        
        header.addStretch()
        
        # Bookmark/Favorite buttons
        self.bookmark_btn = QPushButton("☆ Bookmark")
        self.bookmark_btn.setObjectName("smallBtn")
        self.bookmark_btn.clicked.connect(self.toggle_bookmark)
        header.addWidget(self.bookmark_btn)
        
        self.favorite_btn = QPushButton("♥ Favorite")
        self.favorite_btn.setObjectName("smallBtn")
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        header.addWidget(self.favorite_btn)
        
        layout.addLayout(header)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Astrological info
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(8)
        
        # Day info card
        info_card = QFrame()
        info_card.setObjectName("card")
        info_layout = QVBoxLayout(info_card)
        
        self.day_ruler_label = QLabel()
        self.day_ruler_label.setObjectName("section")
        info_layout.addWidget(self.day_ruler_label)
        
        self.moon_label = QLabel()
        self.moon_label.setObjectName("mansion")
        info_layout.addWidget(self.moon_label)
        
        self.hours_text = QLabel()
        self.hours_text.setObjectName("small")
        self.hours_text.setWordWrap(True)
        info_layout.addWidget(self.hours_text)
        
        left_layout.addWidget(info_card)
        
        # Recommendations card
        rec_card = QFrame()
        rec_card.setObjectName("card")
        rec_layout = QVBoxLayout(rec_card)
        
        rec_title = QLabel("Recommended Activities")
        rec_title.setObjectName("section")
        rec_layout.addWidget(rec_title)
        
        self.rec_list = QLabel()
        self.rec_list.setWordWrap(True)
        self.rec_list.setStyleSheet("color: #8bc34a;")
        rec_layout.addWidget(self.rec_list)
        
        avoid_title = QLabel("Avoid")
        avoid_title.setObjectName("section")
        avoid_title.setStyleSheet("color: #e57373;")
        rec_layout.addWidget(avoid_title)
        
        self.avoid_list = QLabel()
        self.avoid_list.setWordWrap(True)
        self.avoid_list.setStyleSheet("color: #e57373;")
        rec_layout.addWidget(self.avoid_list)
        
        left_layout.addWidget(rec_card)
        
        # Picatrix References
        ref_card = QFrame()
        ref_card.setObjectName("card")
        ref_layout = QVBoxLayout(ref_card)
        
        ref_title = QLabel("Picatrix References")
        ref_title.setObjectName("section")
        ref_layout.addWidget(ref_title)
        
        self.ref_text = QLabel()
        self.ref_text.setObjectName("small")
        self.ref_text.setWordWrap(True)
        ref_layout.addWidget(self.ref_text)
        
        left_layout.addWidget(ref_card)
        left_layout.addStretch()
        
        splitter.addWidget(left_panel)
        
        # Right panel: Diary, Tasks, Dreams
        right_panel = QTabWidget()
        
        # Diary tab
        diary_tab = QWidget()
        diary_layout = QVBoxLayout(diary_tab)
        
        diary_label = QLabel("Personal Notes")
        diary_label.setObjectName("section")
        diary_layout.addWidget(diary_label)
        
        self.diary_text = QTextEdit()
        self.diary_text.setPlaceholderText("Write your diary entry for this day...")
        self.diary_text.textChanged.connect(self.save_diary)
        diary_layout.addWidget(self.diary_text)
        
        right_panel.addTab(diary_tab, "📝 Diary")
        
        # Tasks tab
        tasks_tab = QWidget()
        tasks_layout = QVBoxLayout(tasks_tab)
        
        task_header = QHBoxLayout()
        task_label = QLabel("Tasks")
        task_label.setObjectName("section")
        task_header.addWidget(task_label)
        
        task_header.addStretch()
        
        add_task_btn = QPushButton("+ Add")
        add_task_btn.setObjectName("smallBtn")
        add_task_btn.clicked.connect(self.add_task)
        task_header.addWidget(add_task_btn)
        
        tasks_layout.addLayout(task_header)
        
        self.tasks_widget = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_widget)
        self.tasks_layout.setSpacing(4)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.tasks_widget)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        tasks_layout.addWidget(scroll)
        tasks_layout.addStretch()
        
        right_panel.addTab(tasks_tab, "☑ Tasks")
        
        # Dreams tab
        dreams_tab = QWidget()
        dreams_layout = QVBoxLayout(dreams_tab)
        
        dreams_label = QLabel("Dream Journal")
        dreams_label.setObjectName("section")
        dreams_layout.addWidget(dreams_label)
        
        self.dreams_text = QTextEdit()
        self.dreams_text.setPlaceholderText("Record your dreams...")
        self.dreams_text.textChanged.connect(self.save_dream)
        dreams_layout.addWidget(self.dreams_text)
        
        right_panel.addTab(dreams_tab, "🌙 Dreams")
        
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 550])
        
        layout.addWidget(splitter)
    
    def load_day(self):
        self.db = get_database()
        data = get_day_data(self.current_date)
        
        # Header
        self.date_label.setText(self.current_date.strftime('%A, %B %d, %Y'))
        
        # Day info
        ruler = data.get('day_ruler', '')
        ruler_ar = data.get('day_ruler_ar', '')
        self.day_ruler_label.setText(f"Planetary Day: {get_planet_symbol(ruler)} {ruler} ({ruler_ar})")
        
        moon_sign = data.get('moon_sign', '')
        mansion = data.get('moon_mansion', '')
        spirit = data.get('mansion_spirit', '')
        spirit_name = data.get('mansion_spirit_name', '')
        mansion_nature = data.get('mansion_nature', '')
        
        mansion_line = f"☽ Moon: {moon_sign} | Mansion: {mansion}"
        if spirit_name:
            mansion_line += f"\n   Spirit: {spirit_name}"
        if mansion_nature:
            mansion_line += f"  |  Nature: {mansion_nature}"
        self.moon_label.setText(mansion_line)
        
        # Planetary hours (current)
        hours = data.get('planetary_hours', [])
        current_hour_text = ""
        now = datetime.now()
        for h in hours:
            start_h = int(h['start_jd'])
            # Simplified display
        # Show first 6 hours summary
        hour_summary = []
        for h in hours[:6]:
            hour_summary.append(f"H{h['hour_number']+1} {get_planet_symbol(h['planet'])} {h['planet'][:3]} ({h['spirit_name']})")
        self.hours_text.setText("Planetary Hours (day):\n" + "\n".join(hour_summary))
        
        # Recommendations
        recs = data.get('recommendations', [])
        self.rec_list.setText("\n".join(f"• {r}" for r in recs) if recs else "No specific recommendations")
        
        avoids = data.get('avoid', [])
        self.avoid_list.setText("\n".join(f"• {a}" for a in avoids) if avoids else "No specific warnings")
        
        # Picatrix references (dynamic from calendar_engine)
        picatrix_refs = data.get('picatrix_references', [])
        ref_lines = list(picatrix_refs[:6]) if picatrix_refs else [
            "Picatrix Book IV, Ch.5 (Mansions)",
            "Picatrix Book IV, Ch.9 (Images & Spirits)",
            "Picatrix Book III (Planetary Properties)"
        ]
        self.ref_text.setText("\n".join(ref_lines))
        
        # Electional data
        elections = data.get('elections', [])
        elections_text = ""
        if elections:
            elections_text = "Elections:\n"
            for e in elections[:3]:
                op = e.get('operation', '')[:50]
                cat = e.get('category', '') or e.get('rating', '')
                if cat:
                    cat = cat.replace('_', ' ').title()
                elections_text += f"  • {cat + ': ' if cat else ''}{op}\n"
        self.ref_text.setText(
            self.ref_text.text() + ("\n\n" + elections_text if elections_text else "")
        )
        
        # Pliny image info (if available)
        pliny = data.get('pliny_image')
        if pliny:
            pliny_desc = pliny.get('description', '')[:80]
            pliny_mat = pliny.get('material', '')
            pliny_spirit = pliny.get('spirit_name', '')
            pliny_text = f"\nPliny Image: {pliny_desc}"
            if pliny_mat:
                pliny_text += f"\n   Material: {pliny_mat}"
            if pliny_spirit:
                pliny_text += f"\n   Spirit: {pliny_spirit}"
            self.ref_text.setText(self.ref_text.text() + pliny_text)
        
        # Load user data
        date_str = self.current_date.isoformat()
        
        # Diary
        diary_entries = self.db.get_diary_by_date(date_str)
        if diary_entries:
            self.diary_text.setPlainText(diary_entries[0]['content'])
        else:
            self.diary_text.clear()
        
        # Tasks
        self.refresh_tasks()
        
        # Dreams
        dreams = self.db.get_dreams_by_date(date_str)
        if dreams:
            self.dreams_text.setPlainText(dreams[0]['content'])
        else:
            self.dreams_text.clear()
        
        # Bookmark/Favorite status
        bookmarks = self.db.get_bookmarks(date_str)
        self.bookmark_btn.setText("★ Bookmarked" if bookmarks else "☆ Bookmark")
        
        favorites = self.db.get_favorites(date_str)
        self.favorite_btn.setText("♥ Favorited" if favorites else "♥ Favorite")
    
    def refresh_tasks(self):
        # Clear existing tasks
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        date_str = self.current_date.isoformat()
        tasks = self.db.get_tasks(date_str)
        
        for task in tasks:
            task_widget = QWidget()
            task_layout = QHBoxLayout(task_widget)
            task_layout.setContentsMargins(4, 2, 4, 2)
            task_layout.setSpacing(8)
            
            checkbox = QCheckBox()
            checkbox.setChecked(bool(task['done']))
            checkbox.toggled.connect(lambda checked, tid=task['id']: self.toggle_task(tid, checked))
            task_layout.addWidget(checkbox)
            
            label = QLabel(task['text'])
            if task['done']:
                label.setStyleSheet("text-decoration: line-through; color: #888;")
            task_layout.addWidget(label)
            
            task_layout.addStretch()
            
            del_btn = QPushButton("✕")
            del_btn.setObjectName("smallBtn")
            del_btn.setFixedSize(24, 24)
            del_btn.clicked.connect(lambda _, tid=task['id']: self.delete_task(tid))
            task_layout.addWidget(del_btn)
            
            self.tasks_layout.addWidget(task_widget)
        
        self.tasks_layout.addStretch()
    
    def save_diary(self):
        date_str = self.current_date.isoformat()
        content = self.diary_text.toPlainText()
        if content:
            existing = self.db.get_diary_by_date(date_str)
            if existing:
                self.db.update_diary(existing[0]['id'], content)
            else:
                self.db.add_diary(date_str, content)
    
    def save_dream(self):
        date_str = self.current_date.isoformat()
        content = self.dreams_text.toPlainText()
        if content:
            existing = self.db.get_dreams_by_date(date_str)
            if existing:
                self.db.update_dream(existing[0]['id'], content)
            else:
                self.db.add_dream(date_str, content)
    
    def add_task(self):
        text, ok = QInputDialog.getText(self, "Add Task", "Task description:")
        if ok and text.strip():
            self.db.add_task(self.current_date.isoformat(), text.strip())
            self.refresh_tasks()
    
    def toggle_task(self, task_id, checked):
        self.db.toggle_task(task_id)
        self.refresh_tasks()
    
    def delete_task(self, task_id):
        self.db.delete_task(task_id)
        self.refresh_tasks()
    
    def toggle_bookmark(self):
        date_str = self.current_date.isoformat()
        bookmarks = self.db.get_bookmarks(date_str)
        if bookmarks:
            self.db.remove_bookmark(bookmarks[0]['id'])
        else:
            self.db.add_bookmark(date_str, f"Bookmarked {date_str}")
        self.load_day()
    
    def toggle_favorite(self):
        date_str = self.current_date.isoformat()
        favorites = self.db.get_favorites(date_str)
        if favorites:
            self.db.remove_favorite(favorites[0]['id'])
        else:
            self.db.add_favorite(date_str, f"Favorited {date_str}")
        self.load_day()
    
    def prev_day(self):
        self.current_date -= timedelta(days=1)
        self.load_day()
    
    def next_day(self):
        self.current_date += timedelta(days=1)
        self.load_day()
    
    def set_date(self, d):
        self.current_date = d
        self.load_day()


# ─── Week View ────────────────────────────────────────────────────────────────
class WeekView(QWidget):
    day_selected = pyqtSignal(date)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_date = datetime.now().date() - timedelta(days=datetime.now().weekday())
        self.init_ui()
        self.load_week()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header = QHBoxLayout()
        prev_btn = QPushButton("◀ Prev Week")
        prev_btn.setObjectName("smallBtn")
        prev_btn.clicked.connect(self.prev_week)
        header.addWidget(prev_btn)
        
        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        header.addWidget(self.title_label)
        
        next_btn = QPushButton("Next Week ▶")
        next_btn.setObjectName("smallBtn")
        next_btn.clicked.connect(self.next_week)
        header.addWidget(next_btn)
        
        header.addStretch()
        layout.addLayout(header)
        
        # Week grid
        self.grid = QHBoxLayout()
        self.grid.setSpacing(4)
        layout.addLayout(self.grid)
        layout.addStretch()
    
    def load_week(self):
        # Clear
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        week_end = self.start_date + timedelta(days=6)
        self.title_label.setText(f"{self.start_date.strftime('%b %d')} — {week_end.strftime('%b %d, %Y')}")
        
        current = self.start_date
        while current <= week_end:
            day_card = self.create_day_card(current)
            self.grid.addWidget(day_card)
            current += timedelta(days=1)
    
    def create_day_card(self, d):
        card = QFrame()
        card.setObjectName("dayCard")
        card.setFixedWidth(120)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        day_name = d.strftime('%a')
        day_num = d.strftime('%d')
        
        name_lbl = QLabel(day_name)
        name_lbl.setObjectName("small")
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_lbl)
        
        num_lbl = QLabel(day_num)
        num_lbl.setObjectName("dayNum")
        num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(num_lbl)
        
        data = get_day_data(d)
        
        moon_lbl = QLabel(f"☽ {data['moon_sign'][:3]}")
        moon_lbl.setObjectName("small")
        moon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(moon_lbl)
        
        mansion = data.get('moon_mansion', '')
        if mansion:
            m_lbl = QLabel(mansion[:10])
            m_lbl.setObjectName("mansion")
            m_lbl.setFont(QFont("", 9))
            m_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(m_lbl)
        
        ruler = data.get('day_ruler', '')
        r_lbl = QLabel(f"{get_planet_symbol(ruler)} {ruler[:3]}")
        r_lbl.setStyleSheet("color: #d4a843;")
        r_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(r_lbl)
        
        # Aspects count
        aspects = data.get('aspects', [])
        if aspects:
            a_lbl = QLabel(f"{len(aspects)} aspects")
            a_lbl.setObjectName("small")
            a_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(a_lbl)
        
        card.mousePressEvent = lambda e, date=d: self.day_selected.emit(date)
        
        return card
    
    def prev_week(self):
        self.start_date -= timedelta(days=7)
        self.load_week()
    
    def next_week(self):
        self.start_date += timedelta(days=7)
        self.load_week()


# ─── Year View ────────────────────────────────────────────────────────────────
class YearView(QWidget):
    month_selected = pyqtSignal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.year = datetime.now().year
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        header = QHBoxLayout()
        prev_btn = QPushButton("◀")
        prev_btn.setObjectName("smallBtn")
        prev_btn.setFixedSize(36, 36)
        prev_btn.clicked.connect(self.prev_year)
        header.addWidget(prev_btn)
        
        self.title_label = QLabel(str(self.year))
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(self.title_label)
        
        next_btn = QPushButton("▶")
        next_btn.setObjectName("smallBtn")
        next_btn.setFixedSize(36, 36)
        next_btn.clicked.connect(self.next_year)
        header.addWidget(next_btn)
        
        header.addStretch()
        layout.addLayout(header)
        
        # 12 months grid
        months_grid = QGridLayout()
        months_grid.setSpacing(8)
        
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        for i, name in enumerate(month_names):
            row = i // 4
            col = i % 4
            card = self.create_month_card(i + 1, name)
            months_grid.addWidget(card, row, col)
        
        layout.addLayout(months_grid)
        layout.addStretch()
    
    def create_month_card(self, month_num, month_name):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedSize(180, 100)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        
        name_lbl = QLabel(f"{month_name} {self.year}")
        name_lbl.setFont(QFont("", 12, QFont.Weight.Bold))
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_lbl)
        
        # Get summary data
        data = get_month_data(self.year, month_num)
        
        # Count aspects
        total_aspects = sum(len(d.get('aspects', [])) for d in data)
        
        # Most common moon sign
        signs = [d.get('moon_sign', '') for d in data if d.get('moon_sign')]
        most_common = max(set(signs), key=signs.count) if signs else '—'
        
        summary = QLabel(f"{len(data)} days | {total_aspects} aspects\nMost Moon: {most_common}")
        summary.setObjectName("small")
        summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(summary)
        
        card.mousePressEvent = lambda e, m=month_num: self.month_selected.emit(self.year, m)
        
        return card
    
    def prev_year(self):
        self.year -= 1
        self.title_label.setText(str(self.year))
        self.init_ui()
    
    def next_year(self):
        self.year += 1
        self.title_label.setText(str(self.year))
        self.init_ui()


# ─── Search View ──────────────────────────────────────────────────────────────
class SearchView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        title = QLabel("Search")
        title.setObjectName("title")
        layout.addWidget(title)
        
        # Search bar
        search_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search diary, tasks, dreams...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_bar.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.setObjectName("primaryBtn")
        search_btn.clicked.connect(self.perform_search)
        search_bar.addWidget(search_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("smallBtn")
        clear_btn.clicked.connect(self.clear_results)
        search_bar.addWidget(clear_btn)
        
        layout.addLayout(search_bar)
        
        # Recent searches
        recent_label = QLabel("Recent Searches")
        recent_label.setObjectName("section")
        layout.addWidget(recent_label)
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(100)
        self.recent_list.itemClicked.connect(self.recent_search_clicked)
        layout.addWidget(self.recent_list)
        
        # Results
        results_label = QLabel("Results")
        results_label.setObjectName("section")
        layout.addWidget(results_label)
        
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(4)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_area.setWidget(self.results_widget)
        self.results_area.setStyleSheet("QScrollArea { border: none; }")
        layout.addWidget(self.results_area)
        
        self.load_recent_searches()
    
    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
        
        self.db.add_search_history(query)
        results = self.db.search_entries(query)
        
        self.display_results(results, query)
        self.load_recent_searches()
    
    def display_results(self, results, query):
        # Clear
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        total = sum(len(v) for v in results.values())
        
        header = QLabel(f"Found {total} results for '{query}'")
        header.setObjectName("subtitle")
        self.results_layout.addWidget(header)
        
        for category, items in results.items():
            if items:
                cat_label = QLabel(f"── {category.upper()} ({len(items)}) ──")
                cat_label.setObjectName("section")
                self.results_layout.addWidget(cat_label)
                
                for item in items:
                    card = QFrame()
                    card.setObjectName("card")
                    card_layout = QVBoxLayout(card)
                    card_layout.setContentsMargins(8, 8, 8, 8)
                    
                    date_lbl = QLabel(f"📅 {item['date']}")
                    date_lbl.setStyleSheet("color: #d4a843; font-weight: bold;")
                    card_layout.addWidget(date_lbl)
                    
                    content_text = item.get('content', item.get('text', item.get('note', '')))
                    content_lbl = QLabel(content_text[:200])
                    content_lbl.setWordWrap(True)
                    card_layout.addWidget(content_lbl)
                    
                    self.results_layout.addWidget(card)
        
        self.results_layout.addStretch()
    
    def clear_results(self):
        self.search_input.clear()
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.results_layout.addStretch()
    
    def load_recent_searches(self):
        self.recent_list.clear()
        history = self.db.get_search_history(limit=10)
        for item in history:
            QListWidgetItem(item['query'], self.recent_list)
    
    def recent_search_clicked(self, item):
        self.search_input.setText(item.text())
        self.perform_search()


# ─── Bookmarks View ───────────────────────────────────────────────────────────
class BookmarksView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self.init_ui()
        self.load_bookmarks()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        title = QLabel("Bookmarks")
        title.setObjectName("title")
        layout.addWidget(title)
        
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.go_to_date)
        layout.addWidget(self.list_widget)
    
    def load_bookmarks(self):
        self.list_widget.clear()
        bookmarks = self.db.get_all_bookmarks()
        for bm in bookmarks:
            item = QListWidgetItem(f"📌 {bm['date']} — {bm['note'][:50]}")
            item.setData(Qt.ItemDataRole.UserRole, bm['date'])
            self.list_widget.addItem(item)
    
    def go_to_date(self, item):
        date_str = item.data(Qt.ItemDataRole.UserRole)
        # Emit signal or open diary
        pass


# ─── Favorites View ───────────────────────────────────────────────────────────
class FavoritesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self.init_ui()
        self.load_favorites()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        title = QLabel("Favorites")
        title.setObjectName("title")
        layout.addWidget(title)
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
    
    def load_favorites(self):
        self.list_widget.clear()
        favorites = self.db.get_all_favorites()
        for fav in favorites:
            item = QListWidgetItem(f"♥ {fav['date']} — {fav['note'][:50]}")
            item.setData(Qt.ItemDataRole.UserRole, fav['date'])
            self.list_widget.addItem(item)


# ─── Main Window ──────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = get_database()
        self.setWindowTitle("MagiJournal")
        self.setMinimumSize(1200, 800)
        self.resize(1300, 850)
        
        self.init_ui()
        self.apply_theme()
        
        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.auto_save)
        self.save_timer.start(30000)  # 30 seconds
        
        # System tray icon (background notifications)
        self.icon_path = '/home/ladylefey/AstroMage/MagiJournal/picatrix.png'
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(self.icon_path))
        self.tray_icon.setToolTip("🔮 MagiJournal — Cosmic Alerts Active")
        
        tray_menu = QMenu()
        show_action = tray_menu.addAction("🪐 Show MagiJournal")
        show_action.triggered.connect(self.showNormal)
        show_action.triggered.connect(self.raise_)
        show_action.triggered.connect(self.activateWindow)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("✕ Quit")
        quit_action.triggered.connect(self.quit_application)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # ─── Cosmic Alert State (merged from lilly_cosmic_alerts.py) ─────
        self.alert_state_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'magi_alert_state.json'
        )
        self.alert_state = self._load_alert_state()
        
        # In-memory tracking (reset each session)
        self.last_hour_idx = -1
        self._last_notify_ts = 0
        
        # Initial hour display
        self.update_hour_display()
        
        # Cosmic alert timer (every 30 seconds — checks all 4 alert types)
        self.alert_timer = QTimer()
        self.alert_timer.timeout.connect(self.check_cosmic_alerts)
        self.alert_timer.start(30000)  # 30 seconds
    
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #12122a; border-right: 1px solid #2a2a4a;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(2)
        
        # App title
        app_title = QLabel("🔮 MagiJournal")
        app_title.setFont(QFont("", 14, QFont.Weight.Bold))
        app_title.setStyleSheet("color: #d4a843; padding: 16px;")
        sidebar_layout.addWidget(app_title)
        
        # Navigation
        nav_items = [
            ("📅 Month", self.show_month),
            ("📆 Week", self.show_week),
            ("🗓 Year", self.show_year),
            ("✧ Simply Astrology", self.show_simply_astrology),
            ("🔍 Search", self.show_search),
            ("📌 Bookmarks", self.show_bookmarks),
            ("♥ Favorites", self.show_favorites),
        ]
        
        self.nav_buttons = []
        for label, callback in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("navBtn")
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        sidebar_layout.addStretch()
        
        # Current planetary hour (dynamic, updated by timer)
        self.hour_widget = QWidget()
        self.hour_widget.setStyleSheet("background-color: #1a1a2e; border-top: 1px solid #2a2a4a; padding: 12px;")
        hour_layout = QVBoxLayout(self.hour_widget)
        hour_layout.setSpacing(4)
        
        hour_title = QLabel("Current Hour")
        hour_title.setObjectName("small")
        hour_layout.addWidget(hour_title)
        
        self.hour_planet_lbl = QLabel("—")
        self.hour_planet_lbl.setObjectName("planet")
        self.hour_planet_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hour_layout.addWidget(self.hour_planet_lbl)
        
        self.hour_spirit_lbl = QLabel("")
        self.hour_spirit_lbl.setObjectName("small")
        self.hour_spirit_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hour_layout.addWidget(self.hour_spirit_lbl)
        
        sidebar_layout.addWidget(self.hour_widget)
        
        main_layout.addWidget(sidebar)
        
        # Main content area
        self.stack = QStackedWidget()
        
        self.month_view = MonthView()
        self.week_view = WeekView()
        self.year_view = YearView()
        self.simply_astrology_view = SimplyAstrologyView()
        self.search_view = SearchView()
        self.bookmarks_view = BookmarksView()
        self.favorites_view = FavoritesView()
        self.daily_page = DailyDiaryPage()

        self.stack.addWidget(self.month_view)              # 0
        self.stack.addWidget(self.week_view)               # 1
        self.stack.addWidget(self.year_view)               # 2
        self.stack.addWidget(self.simply_astrology_view)   # 3
        self.stack.addWidget(self.search_view)             # 4
        self.stack.addWidget(self.bookmarks_view)          # 5
        self.stack.addWidget(self.favorites_view)          # 6
        self.stack.addWidget(self.daily_page)              # 7
        
        main_layout.addWidget(self.stack)
        
        # Connect signals
        self.month_view.day_selected.connect(self.open_diary)
        self.week_view.day_selected.connect(self.open_diary)
        self.year_view.month_selected.connect(self.open_month)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Set initial view
        self.set_active_nav(0)
        self.show_month()
    
    def set_active_nav(self, index):
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.setObjectName("navBtnActive")
            else:
                btn.setObjectName("navBtn")
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)
    
    def show_month(self):
        self.set_active_nav(0)
        self.stack.setCurrentIndex(0)

    def show_week(self):
        self.set_active_nav(1)
        self.stack.setCurrentIndex(1)

    def show_year(self):
        self.set_active_nav(2)
        self.stack.setCurrentIndex(2)

    def show_simply_astrology(self):
        self.set_active_nav(3)
        self.stack.setCurrentIndex(3)

    def show_search(self):
        self.set_active_nav(4)
        self.stack.setCurrentIndex(4)

    def show_bookmarks(self):
        self.set_active_nav(5)
        self.stack.setCurrentIndex(5)
        self.bookmarks_view.load_bookmarks()

    def show_favorites(self):
        self.set_active_nav(6)
        self.stack.setCurrentIndex(6)
        self.favorites_view.load_favorites()
    
    def open_diary(self, d):
        self.daily_page.set_date(d)
        self.daily_page.load_day()
        self.stack.setCurrentIndex(7)
    
    def open_month(self, year, month):
        self.month_view.year = year
        self.month_view.month = month
        self.month_view.load_month_data()
        self.show_month()
    
    def apply_theme(self):
        self.setStyleSheet(STYLESHEET)
    
    def auto_save(self):
        self.statusBar().showMessage("Auto-saved", 2000)
    
    def update_hour_display(self):
        """Update the sidebar hour labels and return the current hour number or -1."""
        from datetime import datetime, timezone, timedelta
        from calendar_engine import get_day_data
        import swisseph as swe

        TZ = timezone(timedelta(hours=2))
        now = datetime.now(TZ)
        data = get_day_data(now.date())
        hours_data = data.get('planetary_hours', [])

        if not hours_data:
            self.hour_planet_lbl.setText("—")
            self.hour_spirit_lbl.setText("")
            return -1

        utc = now.astimezone(timezone.utc)
        now_jd = swe.julday(utc.year, utc.month, utc.day,
                            utc.hour + now.minute / 60 + now.second / 3600)

        for h in hours_data:
            if h['start_jd'] <= now_jd < h['end_jd']:
                self.hour_planet_lbl.setText(
                    f"{get_planet_symbol(h['planet'])} {h['planet']}")
                self.hour_spirit_lbl.setText(h['spirit_name'])
                return h['hour_number']

        self.hour_planet_lbl.setText("—")
        self.hour_spirit_lbl.setText("")
        return -1

    # ─── Alert State Persistence ───────────────────────────────────────────
    def _load_alert_state(self):
        """Load persisted alert state from JSON file."""
        try:
            with open(self.alert_state_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_alert_state(self):
        """Save alert state to JSON file."""
        try:
            with open(self.alert_state_file, 'w') as f:
                json.dump(self.alert_state, f, indent=2)
        except Exception:
            pass

    # ─── Centralized Notification ──────────────────────────────────────────
    def _send_notification(self, title, body, timeout_ms=0):
        """Send desktop notification with MagiJournal icon and style.
        Stays on screen until dismissed by the user (timeout_ms=0 = never expire)."""
        env = os.environ.copy()
        if 'DBUS_SESSION_BUS_ADDRESS' not in env:
            env['DBUS_SESSION_BUS_ADDRESS'] = 'unix:path=/run/user/1000/bus'
        if 'DISPLAY' not in env:
            env['DISPLAY'] = ':0.0'
        try:
            subprocess.run(
                ['notify-send', '--urgency=normal', '--app-name=MagiJournal',
                 '-t', str(timeout_ms), title, body,
                 '-i', self.icon_path],
                timeout=5, env=env
            )
        except Exception:
            pass

    # ─── Cosmic Alert Checks ───────────────────────────────────────────────
    # ─── Lookup tables for rich notifications ────────────────────────────
    _PLANET_ELEMENTS = {
        'Sun': '🔥 Fire', 'Moon': '💧 Water', 'Mercury': '🌬 Air',
        'Venus': '💧 Water', 'Mars': '🔥 Fire', 'Jupiter': '🌬 Air',
        'Saturn': '🌍 Earth'
    }

    _NAKSHATRAS = [
        'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
        'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
        'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
        'Mula', 'Purva Ashada', 'Uttara Ashada', 'Shravana', 'Dhanishta', 'Shatabhisha',
        'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
    ]

    _PLANET_ENERGY = {
        'Sun': 'Vitality, radiance, and sovereign will — time to lead',
        'Moon': 'Emotion, intuition, and deep feeling — go inward',
        'Mercury': 'Thought, movement, and exchange — speak and connect',
        'Venus': 'Beauty, love, and harmony — soften and receive',
        'Mars': 'Drive, courage, and assertion — act with purpose',
        'Jupiter': 'Expansion, wisdom, and fortune — grow and trust',
        'Saturn': 'Discipline, structure, and karma — build what endures'
    }

    def _get_most_tight_aspect(self, data):
        """Return the tightest aspect as a formatted string, or empty."""
        aspects = data.get('aspects', [])
        if not aspects:
            return ''
        best = min(aspects, key=lambda a: float(a.get('orb', 999)))
        orb = float(best['orb'])
        applying = best.get('applying', '')
        return f"{best['symbol']} {best['p1']} {best['aspect']} {best['p2']} ({orb:.1f}°{', ' + applying if applying else ''})"

    def _check_planetary_hour(self, now, data):
        """
        Check if the planetary hour changed.
        When it does, send a SINGLE rich notification with ALL celestial data.
        """
        import swisseph as swe

        hours_data = data.get('planetary_hours', [])
        if not hours_data:
            return None

        utc = now.astimezone(timezone.utc)
        now_jd = swe.julday(utc.year, utc.month, utc.day,
                            utc.hour + now.minute / 60 + now.second / 3600)

        current_hour = None
        for h in hours_data:
            if h['start_jd'] <= now_jd < h['end_jd']:
                current_hour = h
                break

        if current_hour is None:
            return None

        new_idx = current_hour['hour_number']

        # Update sidebar display regardless
        self.hour_planet_lbl.setText(
            f"{get_planet_symbol(current_hour['planet'])} {current_hour['planet']}")
        self.hour_spirit_lbl.setText(current_hour['spirit_name'])

        # Notify only on actual hour change (skip first run, debounce 60s)
        notifying = False
        if new_idx != self.last_hour_idx and self.last_hour_idx != -1:
            now_ts = __import__('time').time()
            if hasattr(self, '_last_notify_ts') and (now_ts - self._last_notify_ts) < 60:
                self.last_hour_idx = new_idx
                return None

            # ─── Gather all the data ───────────────────────────────────
            planet = current_hour['planet']
            symbol = get_planet_symbol(planet)
            hour_num = current_hour['hour_number'] + 1

            # Planet info
            element = self._PLANET_ELEMENTS.get(planet, '')
            energy = self._PLANET_ENERGY.get(planet, '')

            # Malikah / Djinn
            spirit = current_hour.get('spirit_name', '—')
            spirit_ar = current_hour.get('spirit_arabic', '')

            # Nakshatra
            mansion_idx = data.get('mansion_index', -1)
            nakshatra = self._NAKSHATRAS[mansion_idx] if 0 <= mansion_idx < len(self._NAKSHATRAS) else '—'
            picatrix_mansion = data.get('moon_mansion', '—')
            mansion_nature = data.get('mansion_nature', '')

            # Important aspect
            aspect_str = self._get_most_tight_aspect(data)

            # ─── Build the rich notification ──────────────────────────
            parts = [
                f"{symbol} {planet} · Hour {hour_num} of the Day",
                f"Jinn/Malikah: {spirit}{' (' + spirit_ar + ')' if spirit_ar else ''}",
                f"Element: {element}" if element else '',
                f"🌙 Nakshatra: {nakshatra} ({picatrix_mansion})",
            ]
            if mansion_nature:
                parts.append(f"   Mansion nature: {mansion_nature}")

            # Energy description
            parts.append('')
            parts.append(f"✦ {energy}")

            # Important aspect
            if aspect_str:
                parts.append(f"✨ Key aspect: {aspect_str}")

            # Filter empty lines
            msg_lines = [p for p in parts if p]
            notification_body = '\n'.join(msg_lines)

            self._send_notification('🪐 Cosmic Hour Change', notification_body)
            self._last_notify_ts = now_ts
            notifying = True

        self.last_hour_idx = new_idx

        if notifying:
            return f"🪐 Hour {new_idx + 1} — {current_hour['planet']} · {current_hour['spirit_name']}"
        return None

    def _check_lunar_mansion(self, now, data):
        """Check if the lunar mansion changed. Returns alert string or None."""
        mansion_idx = data.get('mansion_index', -1)
        mansion_name = data.get('moon_mansion', '')
        mansion_spirit = data.get('mansion_spirit_name', '')
        mansion_nature = data.get('mansion_nature', '')

        mansion_key = f"mansion_{now.strftime('%Y-%m-%d')}_{mansion_idx}"

        if self.alert_state.get('last_mansion_key') != mansion_key:
            nature_str = f" | Nature: {mansion_nature}" if mansion_nature else ""
            msg = (
                f"Mansion #{mansion_idx + 1}: {mansion_name}\n"
                f"Spirit: {mansion_spirit}{nature_str}"
            )
            self._send_notification('🌙 New Lunar Mansion', msg)
            self.alert_state['last_mansion_key'] = mansion_key
            self._save_alert_state()
            return f"🌙 Mansion #{mansion_idx + 1} — {mansion_name}"

        return None

    def _check_new_aspects(self, now, data):
        """Check for new major aspects entering orb. Returns alert string or None."""
        aspects = data.get('aspects', [])
        aspect_keys = [f"{a['p1']}_{a['p2']}_{a['aspect']}" for a in aspects]

        prev_keys = set(self.alert_state.get('last_aspect_keys', []))
        current_set = set(aspect_keys)
        new_keys = current_set - prev_keys

        self.alert_state['last_aspect_keys'] = aspect_keys
        self._save_alert_state()

        if new_keys:
            new_aspects = [a for a in aspects
                           if f"{a['p1']}_{a['p2']}_{a['aspect']}" in new_keys]
            aspects_text = "\n".join(
                f"  {a['symbol']} {a['p1']} {a['aspect']} {a['p2']} ({a['orb']}°)"
                for a in new_aspects[:5]
            )
            msg = f"New aspects in orb:\n{aspects_text}"
            self._send_notification('✨ New Transit Aspects', msg)
            return f"✨ {len(new_aspects)} new aspect(s) entered orb"

        return None

    def _check_dusk_dawn(self, now, data):
        """Check for sunrise/sunset boundary crossing. Returns alert string or None."""
        sunrise_str = data.get('sunrise', '')
        sunset_str = data.get('sunset', '')
        day_key = f"day_{now.strftime('%Y-%m-%d')}"

        if self.alert_state.get('last_day_key') != day_key:
            self.alert_state['last_day_key'] = day_key

        # Strip timezone suffix (e.g. "06:45 SAST" -> "06:45")
        sunrise_clean = sunrise_str.split(' ')[0]
        sunset_clean = sunset_str.split(' ')[0]

        try:
            sunrise_h, sunrise_m = map(int, sunrise_clean.split(':'))
            sunset_h, sunset_m = map(int, sunset_clean.split(':'))
        except (ValueError, IndexError):
            return None

        sunrise_min = sunrise_h * 60 + sunrise_m
        sunset_min = sunset_h * 60 + sunset_m
        now_min = now.hour * 60 + now.minute

        if abs(now_min - sunrise_min) <= 15 and self.alert_state.get('last_sunrise_notify') != day_key:
            self._send_notification('☀️ Sunrise', f"Sunrise at {sunrise_str}")
            self.alert_state['last_sunrise_notify'] = day_key
            self._save_alert_state()
            return f"☀️ Sunrise at {sunrise_str}"

        if abs(now_min - sunset_min) <= 15 and self.alert_state.get('last_sunset_notify') != day_key:
            self._send_notification('🌅 Sunset', f"Sunset at {sunset_str}")
            self.alert_state['last_sunset_notify'] = day_key
            self._save_alert_state()
            return f"🌅 Sunset at {sunset_str}"

        return None

    # ─── Main Alert Loop (replaces check_hour_change) ──────────────────────
    def check_cosmic_alerts(self):
        """
        Called by timer every 30 seconds. Checks all alert types:
        1. Planetary hour change
        2. Lunar mansion transition
        3. New aspects entering orb
        4. Sunrise/sunset boundary
        """
        from datetime import datetime, timezone, timedelta
        from calendar_engine import get_day_data
        import swisseph as swe

        TZ = timezone(timedelta(hours=2))
        now = datetime.now(TZ)
        data = get_day_data(now.date())

        alerts = []

        # 1. Planetary hour (the original MagiJournal check)
        result = self._check_planetary_hour(now, data)
        if result:
            alerts.append(result)

        # 2. Lunar mansion transition
        result = self._check_lunar_mansion(now, data)
        if result:
            alerts.append(result)

        # 3. New aspects entering orb
        result = self._check_new_aspects(now, data)
        if result:
            alerts.append(result)

        # 4. Sunrise/sunset
        result = self._check_dusk_dawn(now, data)
        if result:
            alerts.append(result)

        if alerts:
            info = "; ".join(alerts)
            self.tray_icon.setToolTip(f"🔮 MagiJournal\n{info}")
            print(f"  🔮 {now.strftime('%H:%M')} — {' | '.join(alerts)}")

    # ─── NOP backward compat (so nothing breaks if called externally) ──────
    def check_hour_change(self):
        """Deprecated — kept for backward compat, delegates to check_cosmic_alerts."""
        self.check_cosmic_alerts()
    
    def quit_application(self):
        """Cleanly quit from tray menu."""
        self._save_alert_state()
        self.tray_icon.hide()
        self.db.close()
        QApplication.instance().quit()
    
    def closeEvent(self, event):
        """Minimize to tray instead of closing."""
        if self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.db.close()
            event.accept()


# ─── Entry Point ──────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MagiJournal")
    app.setOrganizationName("AstroMage")
    
    # Set application-wide font
    font = QFont("Segoe UI", 11)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    window = MainWindow()
    # Start minimized to tray — only the tray icon appears.
    # Right-click the tray icon and choose "Show MagiJournal" to open the window.
    window.hide()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
