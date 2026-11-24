"""
Recursion Algorithm Visualizer (Sum of First N Natural Numbers)
Built with Python and Flet (Flutter-backed modern UI).
"""

import asyncio
import sys
import flet as ft


# -------------------------------------------------------------------------
# STEP 2: CORE ALGORITHM & LOGIC (NO PREMADE FUNCTIONS)
# -------------------------------------------------------------------------

def generate_sum_steps(n: int):
    """
    Simulates recursive calculation of sum(n) = n + sum(n-1) with base case sum(0) = 0.
    Returns a recorded list of call and return step dictionaries.
    """
    steps = []
    total_calls = 0

    def recursive_sum(current_n: int, depth: int) -> int:
        nonlocal total_calls
        total_calls += 1

        # Call step
        if current_n == 0:
            steps.append({
                "type": "call",
                "n": current_n,
                "depth": depth,
                "pending_math": "0",
                "return_value": None,
                "total_calls": total_calls,
                "msg": f"Base case reached: sum(0) called (depth {depth})",
                "code_line": 2,
            })
            val = 0
            steps.append({
                "type": "return",
                "n": current_n,
                "depth": depth,
                "pending_math": "0 = 0",
                "return_value": 0,
                "total_calls": total_calls,
                "msg": "sum(0) returns 0",
                "code_line": 2,
            })
            return val
        else:
            steps.append({
                "type": "call",
                "n": current_n,
                "depth": depth,
                "pending_math": f"{current_n} + sum({current_n - 1})",
                "total_calls": total_calls,  # <--- YEH LINE MISSING THI
                "msg": f"Calling sum({current_n}) (depth {depth})",
                "code_line": 1,
            })

            # Sub-call
            sub_res = recursive_sum(current_n - 1, depth + 1)

            # Return step
            result = current_n + sub_res
            steps.append({
                "type": "return",
                "n": current_n,
                "depth": depth,
                "pending_math": f"{current_n} + {sub_res} = {result}",
                "return_value": result,
                "total_calls": total_calls,
                "msg": f"sum({current_n}) returns {result}",
                "code_line": 3,
            })
            return result

    recursive_sum(n, 0)
    return steps


# -------------------------------------------------------------------------
# STEP 3 & 4: UI AND ANIMATION ENGINE
# -------------------------------------------------------------------------

class RecursionVisualizerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.is_running = False
        self.stop_requested = False

        # Configure page theme and appearance
        self.page.title = "Recursion Algorithm Visualizer"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#0B0F19"  # Deep space navy
        self.page.padding = 20
        self.page.window.width = 1200
        self.page.window.height = 850
        self.page.window.min_width = 950
        self.page.window.min_height = 700

        # Stack cards map: depth -> ft.Container
        self.stack_frames = {}

        self.setup_ui()

    def setup_ui(self):
        # 1. Top Header
        self.header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.AUTO_AWESOME, color="#00F0FF", size=28),
                    ft.Text(
                        "Recursion Visualizer (Python)",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color="#F0F6FC",
                    ),
                    ft.Container(
                        content=ft.Text("SUM OF FIRST N NUMBERS", size=11, weight=ft.FontWeight.W_600, color="#00F0FF"),
                        bgcolor="#003847",
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        border_radius=8,
                        border=ft.Border.all(1, "#00F0FF"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.only(bottom=15),
        )

        # 2. Left Panel: Controls
        self.n_input = ft.TextField(
            label="Input N (Natural Number)",
            value="4",
            width=260,
            text_align=ft.TextAlign.LEFT,
            border_color="#00F0FF",
            focused_border_color="#39FF14",
            keyboard_type=ft.KeyboardType.NUMBER,
            color="#FFFFFF",
        )

        self.speed_slider = ft.Slider(
            min=0.5,
            max=4.0,
            divisions=7,
            value=1.5,
            label="{value}x Speed",
            active_color="#00F0FF",
            inactive_color="#1E293B",
        )

        self.btn_start = ft.Button(
            content="Start / Visualize",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            style=ft.ButtonStyle(
                color="#04101A",
                bgcolor="#00F0FF",
                padding=18,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=self.on_start_clicked,
            width=260,
        )

        self.btn_reset = ft.OutlinedButton(
            content="Reset",
            icon=ft.Icons.REFRESH_ROUNDED,
            style=ft.ButtonStyle(
                color="#94A3B8",
                side=ft.BorderSide(1, "#334155"),
                padding=18,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=self.on_reset_clicked,
            width=260,
        )

        left_control_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Execution Controls", size=18, weight=ft.FontWeight.BOLD, color="#38BDF8"),
                    ft.Divider(color="#1E293B", height=15),
                    ft.Text("Algorithm Input", size=13, color="#94A3B8"),
                    self.n_input,
                    ft.Container(height=10),
                    ft.Row(
                        controls=[
                            ft.Text("Animation Speed", size=13, color="#94A3B8"),
                            ft.Icon(ft.Icons.SPEED_ROUNDED, size=16, color="#00F0FF"),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.speed_slider,
                    ft.Container(height=15),
                    self.btn_start,
                    self.btn_reset,
                ],
                spacing=12,
            ),
            bgcolor="#111827",
            border_radius=16,
            border=ft.Border.all(1, "#1E293B"),
            padding=20,
            width=300,
        )

        # Stats Cards
        self.stat_current_call = ft.Text("None", size=16, weight=ft.FontWeight.BOLD, color="#38BDF8")
        self.stat_total_calls = ft.Text("0", size=16, weight=ft.FontWeight.BOLD, color="#A855F7")
        self.stat_final_result = ft.Text("--", size=22, weight=ft.FontWeight.BOLD, color="#39FF14")

        stats_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Real-Time Telemetry", size=15, weight=ft.FontWeight.BOLD, color="#E2E8F0"),
                    ft.Divider(color="#1E293B", height=10),
                    ft.Row(
                        [
                            ft.Text("Active Call:", size=13, color="#94A3B8"),
                            self.stat_current_call,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Text("Total Calls Made:", size=13, color="#94A3B8"),
                            self.stat_total_calls,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Text("Current Output:", size=13, color="#94A3B8"),
                            self.stat_final_result,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=10,
            ),
            bgcolor="#111827",
            border_radius=16,
            border=ft.Border.all(1, "#1E293B"),
            padding=20,
            width=300,
        )

        # 3. Right Panel: Stack & Logs
        # Call Stack Column
        self.stack_column = ft.Column(
            controls=[],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )

        self.stack_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.LAYERS_ROUNDED, color="#00F0FF", size=20),
                            ft.Text("Call Stack Frames (Memory)", size=16, weight=ft.FontWeight.BOLD, color="#E2E8F0"),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Divider(color="#1E293B", height=12),
                    ft.Container(
                        content=self.stack_column,
                        expand=True,
                        alignment=ft.Alignment.TOP_CENTER,
                    ),
                ],
                expand=True,
            ),
            bgcolor="#0E1626",
            border_radius=16,
            border=ft.Border.all(1, "#1E293B"),
            padding=16,
            expand=3,
        )

        # Event Log ListView
        self.log_list = ft.ListView(
            controls=[],
            spacing=8,
            auto_scroll=True,
            expand=True,
        )

        self.log_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.TERMINAL_ROUNDED, color="#39FF14", size=20),
                            ft.Text("Execution Event Log", size=16, weight=ft.FontWeight.BOLD, color="#E2E8F0"),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Divider(color="#1E293B", height=12),
                    self.log_list,
                ],
                expand=True,
            ),
            bgcolor="#0E1626",
            border_radius=16,
            border=ft.Border.all(1, "#1E293B"),
            padding=16,
            expand=2,
        )

        # 4. Bottom Panel: Pseudo-code Highlighting
        self.code_line1 = ft.Container(
            content=ft.Text("1:  def sum(n):", font_family="Consolas, monospace", size=14, color="#E2E8F0"),
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            border_radius=6,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        self.code_line2 = ft.Container(
            content=ft.Text("2:      if n == 0: return 0", font_family="Consolas, monospace", size=14, color="#E2E8F0"),
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            border_radius=6,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        self.code_line3 = ft.Container(
            content=ft.Text("3:      return n + sum(n - 1)", font_family="Consolas, monospace", size=14, color="#E2E8F0"),
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            border_radius=6,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )

        bottom_code_card = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CODE_ROUNDED, color="#F59E0B", size=20),
                                        ft.Text("Live Trace / Pseudo-code Execution", size=15, weight=ft.FontWeight.BOLD, color="#F59E0B"),
                                    ]
                                ),
                                ft.Row(
                                    controls=[self.code_line1, self.code_line2, self.code_line3],
                                    spacing=20,
                                ),
                            ],
                            spacing=6,
                        ),
                        expand=True,
                    ),
                ],
            ),
            bgcolor="#111827",
            border_radius=14,
            border=ft.Border.all(1, "#1E293B"),
            padding=ft.Padding.all(14),
        )

        # Assembly
        main_content = ft.Row(
            controls=[
                ft.Column(
                    controls=[left_control_card, stats_card],
                    spacing=16,
                    width=300,
                ),
                ft.Row(
                    controls=[self.stack_container, self.log_container],
                    spacing=16,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=16,
        )

        self.page.add(
            self.header,
            main_content,
            bottom_code_card,
        )

    def highlight_code_line(self, line_num: int):
        lines = [self.code_line1, self.code_line2, self.code_line3]
        for idx, line in enumerate(lines, 1):
            if idx == line_num:
                line.bgcolor = "#1E3A8A"  # Neon blue-navy active highlight
                line.border = ft.Border.all(1, "#38BDF8")
            else:
                line.bgcolor = "transparent"
                line.border = None

    def add_log_entry(self, msg: str, is_call: bool, is_final: bool = False):
        color = "#00F0FF" if is_call else ("#39FF14" if not is_final else "#FACC15")
        icon = ft.Icons.CALL_MADE_ROUNDED if is_call else (ft.Icons.CALL_RECEIVED_ROUNDED if not is_final else ft.Icons.EMOJI_EVENTS_ROUNDED)

        entry = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=15, color=color),
                    ft.Text(msg, size=13, color="#F1F5F9", weight=ft.FontWeight.W_500 if not is_final else ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=8,
            ),
            bgcolor="#172236",
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            border_radius=8,
            border=ft.Border.all(1, color if is_final else "#1E293B"),
        )
        self.log_list.controls.append(entry)

    def create_stack_frame_widget(self, n: int, depth: int, pending_math: str) -> ft.Container:
        """Creates an animated glassmorphic card representing a recursive stack frame."""
        frame = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(f"depth {depth}", size=11, color="#64748B", weight=ft.FontWeight.BOLD),
                        bgcolor="#0F172A",
                        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                        border_radius=6,
                    ),
                    ft.Text(f"sum({n})", size=15, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    ft.VerticalDivider(color="#334155"),
                    ft.Text(pending_math, size=14, color="#38BDF8", weight=ft.FontWeight.W_500),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=480,
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            bgcolor="#14213D",
            border_radius=12,
            border=ft.Border.all(2, "#00F0FF"),  # Glowing cyan active call border
            scale=ft.Scale(1.05),
            opacity=0.0,
            animate=ft.Animation(350, ft.AnimationCurve.EASE_OUT_BACK),
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            animate_scale=ft.Animation(350, ft.AnimationCurve.EASE_OUT_BACK),
        )
        return frame

    def on_reset_clicked(self, e):
        self.stop_requested = True
        self.is_running = False
        self.stack_frames.clear()
        self.stack_column.controls.clear()
        self.log_list.controls.clear()
        self.stat_current_call.value = "None"
        self.stat_total_calls.value = "0"
        self.stat_final_result.value = "--"
        self.stat_final_result.color = "#39FF14"
        self.highlight_code_line(0)
        self.btn_start.disabled = False
        self.page.update()

    async def on_start_clicked(self, e):
        if self.is_running:
            return

        try:
            n_val = int(self.n_input.value.strip())
            if n_val < 0:
                raise ValueError("N must be non-negative")
            if n_val > 15:
                # Prevent extreme recursion overflow in visualization
                self.add_log_entry("Please enter N <= 15 for optimal visual clarity.", is_call=False)
                self.page.update()
                return
        except ValueError:
            self.add_log_entry("Invalid input! Please enter a valid positive integer.", is_call=False)
            self.page.update()
            return

        self.on_reset_clicked(None)
        self.stop_requested = False
        self.is_running = True
        self.btn_start.disabled = True
        self.page.update()

        steps = generate_sum_steps(n_val)

        for step in steps:
            if self.stop_requested:
                break

            speed = self.speed_slider.value
            delay = 1.0 / max(speed, 0.1)

            step_type = step["type"]
            n = step["n"]
            depth = step["depth"]
            total_calls = step["total_calls"]
            msg = step["msg"]
            code_line = step["code_line"]

            # Highlight code line
            self.highlight_code_line(code_line)
            self.stat_total_calls.value = str(total_calls)
            self.stat_current_call.value = f"sum({n})"

            if step_type == "call":
                # Create and animate new call stack block
                frame = self.create_stack_frame_widget(n, depth, step["pending_math"])
                # Stack visualization: newest call on top
                self.stack_column.controls.insert(0, frame)
                self.stack_frames[depth] = frame
                self.add_log_entry(msg, is_call=True)

                self.page.update()
                await asyncio.sleep(0.05)

                # Animate entrance: slide up / fade in
                frame.opacity = 1.0
                frame.scale = ft.Scale(1.0)
                self.page.update()

            elif step_type == "return":
                ret_val = step["return_value"]
                pending_math = step.get("pending_math", str(ret_val))
                self.stat_final_result.value = str(ret_val)

                self.add_log_entry(msg, is_call=False)

                # Active resolving frame turns vibrant neon green
                if depth in self.stack_frames:
                    target_frame = self.stack_frames[depth]
                    target_frame.bgcolor = "#064E3B"  # Glowing emerald
                    target_frame.border = ft.Border.all(2, "#10B981")
                    target_frame.scale = ft.Scale(1.04)

                    # Update inner text to show return result
                    row_content = target_frame.content
                    row_content.controls[3].value = pending_math
                    row_content.controls[3].color = "#34D399"

                self.page.update()
                await asyncio.sleep(delay * 0.7)

                # Return value moving up animation: remove child frame
                if depth in self.stack_frames:
                    target_frame = self.stack_frames.pop(depth)
                    target_frame.opacity = 0.0
                    target_frame.scale = ft.Scale(0.9)
                    self.page.update()
                    await asyncio.sleep(0.2)
                    if target_frame in self.stack_column.controls:
                        self.stack_column.controls.remove(target_frame)

                # If parent exists, illuminate parent as receiving the resolved value
                parent_depth = depth - 1
                if parent_depth in self.stack_frames:
                    parent_frame = self.stack_frames[parent_depth]
                    parent_frame.border = ft.Border.all(2, "#39FF14")
                    parent_frame.scale = ft.Scale(1.03)
                    self.page.update()
                    await asyncio.sleep(0.15)
                    parent_frame.scale = ft.Scale(1.0)

            self.page.update()
            await asyncio.sleep(delay)

        # Finished
        if not self.stop_requested:
            final_ans = (n_val * (n_val + 1)) // 2
            self.highlight_code_line(0)
            self.stat_current_call.value = "Completed"
            self.stat_final_result.value = f"{final_ans}"
            self.stat_final_result.color = "#00F0FF"

            self.add_log_entry(f"Recursion Complete! Final Result: sum({n_val}) = {final_ans}", is_call=False, is_final=True)
            self.page.update()

        self.btn_start.disabled = False
        self.is_running = False
        self.page.update()


def main(page: ft.Page):
    RecursionVisualizerApp(page)


if __name__ == "__main__":
    ft.run(main)