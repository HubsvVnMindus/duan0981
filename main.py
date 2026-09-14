# -*- coding: utf-8 -*-
"""HTOOL NOVA Android launcher.

The original HTOOL logic lives in htool_core.py and is executed unchanged.
This file only provides an Android terminal-like input/output surface.
"""
import os
import re
import sys
import runpy
import queue
import threading
import traceback
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.metrics import dp

ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
RICH_TAG_RE = re.compile(r"\[(?:/?[a-zA-Z0-9_ #.=:-]+)\]")


class AndroidTerminal:
    def __init__(self):
        self.lines = queue.Queue()
        self.inputs = queue.Queue()
        self.app = None

    def write(self, text):
        if text:
            self.lines.put(str(text))
            Clock.schedule_once(lambda dt: self.flush(), 0)

    def flush(self):
        if not self.app:
            return
        chunks = []
        while True:
            try:
                chunks.append(self.lines.get_nowait())
            except queue.Empty:
                break
        if not chunks:
            return
        text = ''.join(chunks)
        text = ANSI_RE.sub('', text)
        # Some plain print() calls in the original source contain Rich markup.
        text = RICH_TAG_RE.sub('', text)
        self.app.output.text += text
        self.app.output.cursor = (0, len(self.app.output.text))

    def get_input(self, prompt=''):
        self.write('\n' + str(prompt) + ' ')
        return self.inputs.get()


terminal = AndroidTerminal()


class CaptureStdout:
    def write(self, s):
        terminal.write(s)
        return len(s)

    def flush(self):
        pass


class CaptureStderr(CaptureStdout):
    pass


def android_console_input(self, prompt='', password=False, stream=None, **kwargs):
    # Rich Prompt/Confirm/IntPrompt/FloatPrompt all validate the value after
    # Console.input returns, so we only replace the physical input mechanism.
    return terminal.get_input(prompt)


class HtoolApp(App):
    title = 'HTOOL NOVA'

    def build(self):
        Window.softinput_mode = 'below_target'
        root = BoxLayout(orientation='vertical', padding=dp(6), spacing=dp(5))

        header = BoxLayout(size_hint_y=None, height=dp(42))
        title = Label(text='♛ HTOOL NOVA  •  ANDROID', bold=True, font_size='16sp')
        header.add_widget(title)
        clear_btn = Button(text='CLEAR', size_hint_x=None, width=dp(75))
        clear_btn.bind(on_release=lambda *_: self.clear_output())
        header.add_widget(clear_btn)
        root.add_widget(header)

        self.output = TextInput(
            text='', readonly=True, multiline=True,
            font_name='RobotoMono', font_size='11sp',
            background_color=(0.04, 0.05, 0.08, 1),
            foreground_color=(0.92, 0.95, 0.98, 1),
            cursor_blink=False,
        )
        root.add_widget(self.output)

        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(5))
        self.input_box = TextInput(
            multiline=False, hint_text='Nhập lệnh / lựa chọn...', font_size='14sp',
            background_color=(0.08, 0.10, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
        )
        self.input_box.bind(on_text_validate=self.submit)
        row.add_widget(self.input_box)
        send = Button(text='SEND', size_hint_x=None, width=dp(80))
        send.bind(on_release=self.submit)
        row.add_widget(send)
        root.add_widget(row)

        terminal.app = self
        sys.stdout = CaptureStdout()
        sys.stderr = CaptureStderr()

        threading.Thread(target=self.run_original, daemon=True).start()
        return root

    def submit(self, *_):
        value = self.input_box.text
        self.input_box.text = ''
        terminal.inputs.put(value)

    def clear_output(self):
        self.output.text = ''

    def run_original(self):
        try:
            # Keep all relative files (accounts.json, key files, configs, etc.)
            # inside Android's app-private writable directory.
            data_dir = Path(self.user_data_dir)
            data_dir.mkdir(parents=True, exist_ok=True)
            os.chdir(data_dir)

            # Rich's Console.input is the only interactive bridge needed by
            # Prompt/Confirm/IntPrompt/FloatPrompt. The original logic is not
            # rewritten; only the terminal transport is replaced.
            from rich.console import Console
            Console.input = android_console_input

            original = Path(__file__).with_name('htool_core.py')
            runpy.run_path(str(original), run_name='__main__')
        except SystemExit as exc:
            terminal.write(f'\n[HTOOL] Chương trình kết thúc: {exc}\n')
        except Exception:
            terminal.write('\n===== LỖI HTOOL =====\n')
            terminal.write(traceback.format_exc())


if __name__ == '__main__':
    HtoolApp().run()
