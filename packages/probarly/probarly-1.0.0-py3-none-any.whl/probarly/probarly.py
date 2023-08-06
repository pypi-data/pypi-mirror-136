#!/bin/env python3
"""Create beautiful, heavily customizable progress bars... probarly"""
import time
from typing import Any, Dict, List, TypeVar

AnimationType = TypeVar("AnimationType")
TaskType = TypeVar("TaskType")


class Task:
    """Define a task."""

    def __init__(self, text: str, id_: int):
        """Store the id and the text of a task."""
        self.id_ = id_
        self.text = text

    def __hash__(self) -> int:
        return hash(self.id_)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if self.id_ == other.id_:
            return True
        else:
            return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq(other)


class Animation:
    """Define an animation. (Don't use to make a custom bar animation)"""

    def __init__(self, frames: List[str], slow: int = 5):
        """Store the speed and frames of the animation."""
        self.frames = frames
        self.slow = slow


class BarAnimations:
    """Contains animations for the progress bar."""

    classic_fill = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
    hash_ = [" ", "#"]


class OtherAnimations:
    """Contains animations for after the progress bar itself."""

    up_down = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
    up_down = Animation(up_down + up_down[::-1])
    spinner_clockwise = Animation(["/", "-", "\\", "|"], 10)
    spinner_counterclockwise = Animation(spinner_clockwise.frames[::-1], 10)
    morph = Animation(BarAnimations.classic_fill + up_down.frames[::-1])


class Progbar:
    """The progress bar."""

    def __init__(
        self,
        length: int = 10,
        filler: str = " ",
        start: str = "|",
        end: str = "|",
        frames: List[str] = BarAnimations.classic_fill,
        animations: Dict[int, AnimationType] = {"*": OtherAnimations.up_down},
    ):
        """
        How to use:
          - length: specifies length of the progress bar (default 10)
          - filler: what to fill the rest of the progress bar with (default ' ')
          - start: what the start of the progress bar should look like (default '|')
          - end: what the end of the progress bar should look like (default '|')
          - frames: frames for the animation of the progress bar (default BarAnimations.classic_fill)
          - animations: how to use:
             - you can use any task id to specify the animation to use when that task is active
             - an id of -1 is reserved for tasks with no text
             - you can use a '*' to denote all tasks that are not specified in the dict
        """
        self.__animation = Animation([""])
        self.__animation_frame = 0
        self.__frame_index = 0
        self.__full = 0
        self.animations = animations
        self.bar = [frames[0]]
        self.end = end
        self.filler = filler
        self.frames = frames
        self.length = length
        self.start = start
        self.task = Task("", -1)

    def show(self) -> None:
        """Show the current state if the bar."""
        print(
            f"\x1b[1K\r{self.task.text}{self.start}{''.join(self.bar)}{self.filler * (self.length - self.__full - 1)}{self.end} {int(round((self.__full/self.length) * 100))}% {self.__animation.frames[self.__animation_frame]}",
            end="",
        )

    def adv(self, to: int, time_: float = 0.01, task: TaskType = Task("", -1)) -> None:
        """
        How to use:
          - to: a percentage; the bar will go forward that amount
          - time_: the time between switching frames of the progress bar (default 0.005)
          - task: specify a task to show what you are currently doing (default '')
        """
        self.task = task
        for _ in range(int(round((to / 100) * self.length)) * len(self.frames)):
            self.wait(time_)
            if self.bar[-1] in self.frames[:-1]:
                self.bar[-1] = self.frames[self.frames.index(self.bar[-1]) + 1]
            elif self.bar[-1] == self.frames[-1]:
                if self.length - self.__full - 1:
                    self.bar.append(self.frames[0])
                else:
                    self.__full += 1
                    self.show()
                    print()
                    break
                self.__full += 1
            self.show()

    def wait(self, time_: float) -> None:
        """
        How to use:
          - time_: time to wait for
        """
        if self.task.id_ in self.animations:
            self.__animation = self.animations[self.task.id_]
        elif "*" in self.animations:
            self.__animation = self.animations["*"]
        else:
            self.__animation = Animation([""])
        slow = self.__animation.slow
        while time_ >= 0:
            time.sleep(0.005)
            time_ -= 0.005
            self.__frame_index += 1
            if not self.__frame_index % slow:
                self.__animation_frame = (self.__animation_frame + 1) % len(
                    self.__animation.frames
                )
            self.show()

    def reset(self, show_: bool = False) -> None:
        """
        How to use:
          - show_: change to True if you want to show the bar's state after the reset
        """
        self.__animation_frame = 0
        self.__frame_index = 0
        self.__full = 0
        self.bar = [self.frames[0]]
        self.task = ""
        if show_:
            self.show()
