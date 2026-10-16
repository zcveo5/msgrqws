import ctypes
import tkinter as tk
from win32more.Windows.Win32.Graphics import Gdi
from win32more.Windows.Win32.UI.WindowsAndMessaging import (
    GetWindowLongPtrW, SetWindowLongPtrW, GWL_WNDPROC, CallWindowProcW,
    WM_PAINT, WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP, WM_MOUSEWHEEL,
)
from win32more.Windows.Win32.Foundation import HWND, LPARAM, LRESULT, WPARAM, RECT
from ctypes import byref

WNDPROC_PROTO = ctypes.WINFUNCTYPE(LRESULT, HWND, ctypes.c_uint, WPARAM, LPARAM)


class VirtualElement:
    """Base class for immediate-mode GDI elements"""

    def __init__(self, text, x, y, w, h, callback=None):
        self.text = text
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.callback = callback
        self.is_hovered = False
        self.is_pressed = False

    def check_hit(self, mx, my, scroll_y):
        # Adjust check against the current viewport scrolling position
        actual_y = self.y - scroll_y
        return self.x <= mx <= self.x + self.w and actual_y <= my <= actual_y + self.h


class ScrollableFastContainer(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg='black', **kwargs)
        self.update_idletasks()
        self._hwnd = self.winfo_id()

        # Viewport variables
        self.scroll_y = 0
        self.max_scroll = 5000  # Total height of your scrollable layout space
        self.elements = []

        # Populate with 1,000 synthetic interactive rows (Blazing Fast)
        for i in range(1000):
            # Alternate between "Label" blocks and clickable "Buttons"
            if i % 2 == 0:
                self.elements.append(VirtualElement(f"Static Label Block #{i}", 20, i * 45 + 10, 250, 30))
            else:
                idx = i
                self.elements.append(VirtualElement(
                    f"Clickable Button #{idx}", 280, i * 45 + 10, 180, 30,
                    callback=lambda e_idx=idx: print(f"Triggered UI Element action for Button {e_idx}!")
                ))

        # Hook Window Procedure
        self._orig_wnd_ptr = WNDPROC_PROTO(GetWindowLongPtrW(self._hwnd, GWL_WNDPROC))

        def _wndproc(_hwnd, msg, wp, lp):
            res = self._wndproc_wrapper(_hwnd, msg, wp, lp)
            if res is None:
                return CallWindowProcW(self._orig_wnd_ptr, _hwnd, msg, wp, lp)
            return res

        self._new_wndproc = WNDPROC_PROTO(_wndproc)
        wndproc_address = ctypes.cast(self._new_wndproc, ctypes.c_void_p).value
        SetWindowLongPtrW(self._hwnd, GWL_WNDPROC, wndproc_address)

    def _wndproc_wrapper(self, hwnd, msg, wp, lp):
        # Extract mouse coordinates from LPARAM safely
        mx = lp & 0xFFFF
        my = (lp >> 16) & 0xFFFF
        # Handle negative values for signed coordinates if mouse drags out
        if mx > 32768: mx -= 65536
        if my > 32768: my -= 65536

        if msg == WM_PAINT:
            # Let Tcl clean background blocks if it needs to
            #CallWindowProcW(self._orig_wnd_ptr, hwnd, msg, wp, lp)
            self._render_gdi_surface(hwnd)
            return 0

        elif msg == WM_MOUSEWHEEL:
            # High word of WPARAM gives wheel delta (usually 120 or -120)
            delta = (wp >> 16) & 0xFFFF
            if delta > 32768: delta -= 65536

            # Scroll velocity adjustment
            self.scroll_y -= int(delta / 2)
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

            Gdi.InvalidateRect(hwnd, None, True)
            return 0

        elif msg == WM_MOUSEMOVE:
            changed = False
            for elem in self.elements:
                was_hovered = elem.is_hovered
                elem.is_hovered = elem.check_hit(mx, my, self.scroll_y) if elem.callback else False
                if was_hovered != elem.is_hovered:
                    changed = True
            if changed:
                Gdi.InvalidateRect(hwnd, None, True)
            return 0

        elif msg == WM_LBUTTONDOWN:
            for elem in self.elements:
                if elem.callback and elem.check_hit(mx, my, self.scroll_y):
                    elem.is_pressed = True
                    Gdi.InvalidateRect(hwnd, None, True)
            return 0

        elif msg == WM_LBUTTONUP:
            for elem in self.elements:
                if elem.is_pressed:
                    elem.is_pressed = False
                    if elem.check_hit(mx, my, self.scroll_y) and elem.callback:
                        elem.callback()
                    Gdi.InvalidateRect(hwnd, None, True)
            return 0

        return None

    def _render_gdi_surface(self, hwnd):
        # Grab dimensions
        width = self.winfo_width()
        height = self.winfo_height()

        # 1. Double Buffering Setup
        hdc = Gdi.GetDC(hwnd)
        mem_dc = Gdi.CreateCompatibleDC(hdc)
        mem_bitmap = Gdi.CreateCompatibleBitmap(hdc, width, height)
        old_bitmap = Gdi.SelectObject(mem_dc, mem_bitmap)

        # Clear memory canvas canvas background (Solid Deep Dark Grey)
        bg_brush = Gdi.CreateSolidBrush(0x1E1E1E)
        rect = RECT(left=0, top=0, right=width, bottom=height)
        Gdi.FillRect(mem_dc, byref(rect), bg_brush)
        Gdi.DeleteObject(bg_brush)

        # Setup standard font variables
        Gdi.SetBkMode(mem_dc, Gdi.TRANSPARENT)

        # 2. Draw Elements (Virtualized Clipping)
        for elem in self.elements:
            render_y = elem.y - self.scroll_y

            # Optimization: Skip calculating / drawing anything off-screen
            if render_y + elem.h < 0 or render_y > height:
                continue

            # Determine Element Theme styling colors based on interactions
            if not elem.callback:
                # Decorative Label
                box_color = 0x2D2D2D  # Grey
                text_color = 0xCCCCCC  # Light Grey
            else:
                # Interactive button states
                if elem.is_pressed:
                    box_color = 0x00A5FF  # Bright Orange/Cyan active
                    text_color = 0xFFFFFF
                elif elem.is_hovered:
                    box_color = 0x4A4A4A  # Light Hover Highlight
                    text_color = 0x00FFFF  # Yellow/Cyan accent text
                else:
                    box_color = 0x3A3A3A  # Flat Base Button
                    text_color = 0xE0E0E0

            # Render Item Bound Box
            elem_brush = Gdi.CreateSolidBrush(box_color)
            elem_rect = RECT(left=elem.x, top=render_y, right=elem.x + elem.w, bottom=render_y + elem.h)
            Gdi.FillRect(mem_dc, byref(elem_rect), elem_brush)
            Gdi.DeleteObject(elem_brush)

            # Draw Centered Text String
            Gdi.SetTextColor(mem_dc, text_color)
            # Center vertically and horizontally within bounding box
            Gdi.DrawTextW(mem_dc, elem.text, -1, byref(elem_rect),
                          Gdi.DT_CENTER | Gdi.DT_VCENTER | Gdi.DT_SINGLELINE)

        # 3. Fast Blit offscreen buffer directly to hardware graphics viewport
        Gdi.BitBlt(hdc, 0, 0, width, height, mem_dc, 0, 0, Gdi.SRCCOPY)

        # Cleanup memory structures
        Gdi.SelectObject(mem_dc, old_bitmap)
        Gdi.DeleteObject(mem_bitmap)
        Gdi.DeleteDC(mem_dc)
        Gdi.ReleaseDC(hwnd, hdc)


# Test Window Pipeline Setup
root = tk.Tk()
root.title("Immediate GDI Virtual Container (60+ FPS Infinite List)")
root.geometry("500x600")

container = ScrollableFastContainer(root)
container.place(relwidth=1.0, relheight=1.0)

root.mainloop()
