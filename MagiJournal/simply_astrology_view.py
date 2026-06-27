"""
simply_astrology_view.py — Simply Astrology knowledge browser for MagiJournal.

A two-panel widget: section tabs on the left, collapsible knowledge cards
on the right. Loads content from astrology_knowledge.py.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from astrology_knowledge import KNOWLEDGE_SECTIONS, SECTION_NAMES


# ─── Styles ───────────────────────────────────────────────────────
CARD_UNSELECTED = """
    QFrame#sectCard {
        background-color: #1a1a2e;
        border: 1px solid #2a2a4a;
        border-radius: 8px;
        padding: 10px;
        margin: 2px 0px;
    }
    QFrame#sectCard:hover {
        border: 1px solid #d4a843;
        background-color: #1f1f35;
    }
"""
CARD_SELECTED = """
    QFrame#sectCard {
        background-color: #1a1a2e;
        border: 2px solid #d4a843;
        border-radius: 8px;
        padding: 10px;
        margin: 2px 0px;
    }
"""


# ─── Collapsible Knowledge Card ────────────────────────────────────
class KnowledgeCard(QFrame):
    """A single expandable/collapsible knowledge entry card."""

    def __init__(self, heading, body, parent=None):
        super().__init__(parent)
        self.setObjectName("sectCard")
        self.setStyleSheet(CARD_UNSELECTED)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._expanded = False
        self._body = body

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(12, 10, 12, 10)
        self._layout.setSpacing(6)

        # Header row
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        self._expand_icon = QLabel("▶")
        self._expand_icon.setStyleSheet("color: #d4a843; font-size: 12px;")
        self._expand_icon.setFixedWidth(16)
        header_row.addWidget(self._expand_icon)

        self._heading_label = QLabel(heading)
        self._heading_label.setStyleSheet(
            "color: #c77dff; font-weight: bold; font-size: 13px;"
        )
        self._heading_label.setWordWrap(True)
        header_row.addWidget(self._heading_label, 1)

        self._layout.addLayout(header_row)

        # Body (hidden initially)
        self._body_label = QLabel(body)
        self._body_label.setWordWrap(True)
        self._body_label.setStyleSheet(
            "color: #c0c0c0; font-size: 12px; line-height: 1.5; padding: 4px 0px 0px 24px;"
        )
        self._body_label.setVisible(False)
        self._layout.addWidget(self._body_label)

        self.mousePressEvent = lambda e: self.toggle()

    def toggle(self):
        self._expanded = not self._expanded
        self._body_label.setVisible(self._expanded)
        self._expand_icon.setText("▼" if self._expanded else "▶")
        if self._expanded:
            self.setStyleSheet(CARD_SELECTED)
        else:
            self.setStyleSheet(CARD_UNSELECTED)


# ─── Simply Astrology View ─────────────────────────────────────────
class SimplyAstrologyView(QWidget):
    """Main view: section tab buttons on left, knowledge cards on right."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_section = 0
        self._section_btns = []
        self._card_widget = None
        self._card_layout = None
        self._scroll_content = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ─────────────────────────────────────────────
        header = QFrame()
        header.setStyleSheet(
            "background-color: #12122a; border-bottom: 1px solid #2a2a4a;"
        )
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 8)

        title = QLabel("✧ Simply Astrology")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #d4a843;"
        )
        header_layout.addWidget(title)

        subtitle = QLabel(
            "Traditional, Hellenistic & Medieval Islamic Astrology | "
            "Abu Ma'shar · Al-Biruni · Ptolemy · Valens"
        )
        subtitle.setStyleSheet("color: #888; font-size: 11px;")
        header_layout.addWidget(subtitle)

        layout.addWidget(header)

        # ── Section tab buttons ────────────────────────────────
        tab_bar = QFrame()
        tab_bar.setStyleSheet(
            "background-color: #0d0d1a; border-bottom: 1px solid #2a2a4a;"
        )
        tab_scroll = QScrollArea()
        tab_scroll.setWidgetResizable(True)
        tab_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        tab_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        tab_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        tab_container = QWidget()
        tab_container.setStyleSheet("background: transparent;")
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(16, 4, 16, 4)
        tab_layout.setSpacing(4)

        for name in SECTION_NAMES:
            btn = QPushButton(name)
            btn.setObjectName("sectTabBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Fixed,
            )
            btn.clicked.connect(
                lambda checked, idx=len(self._section_btns): self._select_section(idx)
            )
            tab_layout.addWidget(btn)
            self._section_btns.append(btn)

        tab_layout.addStretch()
        tab_scroll.setWidget(tab_container)
        tab_bar_layout = QVBoxLayout(tab_bar)
        tab_bar_layout.setContentsMargins(0, 0, 0, 0)
        tab_bar_layout.addWidget(tab_scroll)
        layout.addWidget(tab_bar)

        # ── Content area ───────────────────────────────────────
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setStyleSheet(
            "QScrollArea { border: none; background-color: #0d0d1a; }"
        )

        self._scroll_content = QWidget()
        self._scroll_content.setStyleSheet("background-color: #0d0d1a;")
        self._card_layout = QVBoxLayout(self._scroll_content)
        self._card_layout.setContentsMargins(24, 12, 24, 24)
        self._card_layout.setSpacing(4)
        self._card_layout.addStretch()

        self._scroll_area.setWidget(self._scroll_content)
        layout.addWidget(self._scroll_area, 1)

        # Apply tab button stylesheet
        self._apply_tab_stylesheet()

        # Select first section
        self._select_section(0)

    def _apply_tab_stylesheet(self):
        for i, btn in enumerate(self._section_btns):
            if i == self._current_section:
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #2a2a4a;
                        color: #d4a843;
                        border: 1px solid #d4a843;
                        border-radius: 14px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    """
                )
            else:
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: transparent;
                        color: #888;
                        border: 1px solid #2a2a4a;
                        border-radius: 14px;
                        padding: 6px 14px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        color: #c77dff;
                        border: 1px solid #c77dff;
                    }
                    """
                )

    def _select_section(self, idx):
        self._current_section = idx
        self._apply_tab_stylesheet()
        self._populate_cards()

    def _populate_cards(self):
        # Clear existing cards (keep the stretch)
        while self._card_layout.count() > 1:
            item = self._card_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        section_name = SECTION_NAMES[self._current_section]
        entries = KNOWLEDGE_SECTIONS.get(section_name, [])

        # Section heading card (always expanded)
        if entries:
            main_heading, main_body = entries[0]
            card = KnowledgeCard(main_heading, main_body)
            card._expanded = True
            card._expand_icon.setText("▼")
            card._body_label.setVisible(True)
            card.setStyleSheet(CARD_SELECTED)
            self._card_layout.insertWidget(
                self._card_layout.count() - 1, card
            )

        # Sub-cards (collapsible)
        for heading, body in entries[1:]:
            card = KnowledgeCard(heading, body)
            self._card_layout.insertWidget(
                self._card_layout.count() - 1, card
            )

        # Scroll to top
        self._scroll_area.verticalScrollBar().setValue(0)
