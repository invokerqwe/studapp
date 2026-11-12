"""Лёгкие графики на canvas Kivy (без matplotlib — он тяжёлый и плохо собирается под Android)."""
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.widget import Widget
from kivymd.app import MDApp


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


class _Chart(Widget):
    data = ListProperty([])
    max_value = NumericProperty(0)      # 0 = авто

    def __init__(self, **kw):
        kw.setdefault("height", dp(220))
        super().__init__(size_hint_y=None, **kw)
        self.bind(pos=self.redraw, size=self.redraw, data=self.redraw, max_value=self.redraw)

    def text(self, txt, cx, y, color, size=11):
        lbl = CoreLabel(text=str(txt), font_size=sp(size))
        lbl.refresh()
        tex = lbl.texture
        Color(*color)
        Rectangle(texture=tex, size=tex.size, pos=(cx - tex.width / 2, y))

    def redraw(self, *_):
        theme = MDApp.get_running_app().theme_cls
        primary, txt, grid = theme.primary_color, theme.text_color, theme.disabled_hint_text_color
        self.canvas.clear()
        with self.canvas:
            if not self.data:
                self.text("Нет данных", self.center_x, self.center_y, txt)
            else:
                self.draw(primary, txt, grid)

    def draw(self, primary, txt, grid):
        raise NotImplementedError


class BarChart(_Chart):
    """data: [(подпись, значение)]"""

    def draw(self, primary, txt, grid):
        data = self.data[:10]
        n = len(data)
        mx = self.max_value or max(v for _, v in data) or 1
        left, bottom = self.x + dp(8), self.y + dp(26)
        w, h = self.width - dp(16), self.height - dp(26) - dp(18)
        slot = w / n
        bw = slot * 0.6
        Color(*grid)
        Line(points=[left, bottom, left + w, bottom], width=1)
        for i, (label, v) in enumerate(data):
            bh = h * min(v / mx, 1)
            x = left + i * slot + (slot - bw) / 2
            Color(*primary)
            Rectangle(pos=(x, bottom), size=(bw, bh))
            self.text(fmt(v), x + bw / 2, bottom + bh + dp(2), txt)
            self.text(str(label)[:9], x + bw / 2, self.y + dp(4), txt, 10)


class LineChart(_Chart):
    """data: [числа] в хронологическом порядке"""

    def draw(self, primary, txt, grid):
        vals = list(self.data)
        n = len(vals)
        mx = self.max_value or max(vals) or 1
        left, bottom = self.x + dp(16), self.y + dp(16)
        w, h = self.width - dp(32), self.height - dp(16) - dp(24)
        Color(*grid)
        Line(points=[left, bottom, left + w, bottom], width=1)
        pts = []
        for i, v in enumerate(vals):
            pts += [left + (w * i / (n - 1) if n > 1 else w / 2), bottom + h * min(v / mx, 1)]
        Color(*primary)
        Line(points=pts, width=dp(1.5))
        r = dp(3)
        for i in range(n):
            x, y = pts[2 * i], pts[2 * i + 1]
            Color(*primary)
            Ellipse(pos=(x - r, y - r), size=(2 * r, 2 * r))
            if n <= 12:
                self.text(fmt(vals[i]), x, y + dp(5), txt, 10)
