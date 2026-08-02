"""按键宏执行引擎。"""

from __future__ import annotations

import threading
import time
from typing import Callable

import keyboard

from config_manager import KeyAction


class MacroEngine:
    """在后台线程中按配置循环触发按键。"""

    def __init__(self, on_state_change: Callable[[bool], None] | None = None) -> None:
        self._running = False
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._on_state_change = on_state_change

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self, actions: list[KeyAction]) -> None:
        if self._running:
            return

        enabled_actions = [action for action in actions if action.enabled]
        if not enabled_actions:
            raise ValueError("没有已启用的按键配置")

        self._stop_event.clear()
        self._running = True
        self._notify_state(True)
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(enabled_actions,),
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if not self._running:
            return

        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._running = False
        self._notify_state(False)

    def toggle(self, actions: list[KeyAction]) -> None:
        if self._running:
            self.stop()
        else:
            self.start(actions)

    def _notify_state(self, running: bool) -> None:
        if self._on_state_change:
            self._on_state_change(running)

    def _run_loop(self, actions: list[KeyAction]) -> None:
        counters = {id(action): 0 for action in actions}
        next_fire = {id(action): time.monotonic() for action in actions}

        while not self._stop_event.is_set():
            now = time.monotonic()
            any_active = False

            for action in actions:
                action_id = id(action)
                if action.repeat_count > 0 and counters[action_id] >= action.repeat_count:
                    continue

                any_active = True
                if now >= next_fire[action_id]:
                    self._press_key(action.key, action.cast_time_ms)
                    counters[action_id] += 1
                    next_fire[action_id] = now + max(action.interval_ms, 10) / 1000.0

            if not any_active:
                break

            if self._stop_event.wait(0.01):
                break

        self._running = False
        self._notify_state(False)

    @staticmethod
    def _press_key(key: str, cast_time_ms: int = 100) -> None:
        normalized = key.strip().lower()
        if not normalized:
            return
        hold_time = max(cast_time_ms, 0) / 1000.0
        try:
            if hold_time <= 0:
                keyboard.press_and_release(normalized)
                return
            keyboard.press(normalized)
            time.sleep(hold_time)
            keyboard.release(normalized)
        except ValueError:
            keyboard.send(normalized)


class HotkeyManager:
    """全局热键监听，用于启停宏。"""

    def __init__(self) -> None:
        self._hotkey_handle = None
        self._callback: Callable[[], None] | None = None

    def register(self, hotkey: str, callback: Callable[[], None]) -> None:
        self.unregister()
        self._callback = callback
        normalized = hotkey.strip().lower()
        self._hotkey_handle = keyboard.add_hotkey(normalized, self._on_hotkey)

    def unregister(self) -> None:
        if self._hotkey_handle is not None:
            keyboard.remove_hotkey(self._hotkey_handle)
            self._hotkey_handle = None
        self._callback = None

    def _on_hotkey(self) -> None:
        if self._callback:
            self._callback()
