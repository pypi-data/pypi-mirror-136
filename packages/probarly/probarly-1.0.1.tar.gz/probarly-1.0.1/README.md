# probarly
more time went into the name than the project (it's probarly not good...)

# how 2
  ## the bar itself
  create a progress bar with `bar = probarly.Progbar()`, args defined below
  <br />
  - length: specifies length of the progress bar (default 10)
  - filler: what to fill the rest of the progress bar with (default ' ')
  - start: what the start of the progress bar should look like (default '|')
  - end: what the end of the progress bar should look like (default '|')
  - frames: frames for the animation of the progress bar (default `BarAnimations.classic_fill`)
  - animations: how to use:
      - you can use any task [id](#tasks) to specify the animation to use when that task is active
      - an [id](#tasks) of -1 is reserved for [tasks](#tasks) with no text
      - you can use a '*' to denote all [tasks](#tasks) that are not specified in the dict
  <br />
  advance the progress bar by a percentage with `bar.adv()`, args defined below
  <br />
  - to: a percentage; the bar will go forward that amount
  - time_: the time between switching frames of the progress bar (default 0.005)
  - [task](#tasks): specify a [task](#tasks) to show what you are currently doing (default `Task("", -1)`)
  <br />
  make the bar stop, with animations still going (use `time.sleep` if you do not want animations) `bar.wait()`, args defined below
  <br />
  - time_: time to wait
  <br />
  reset the progress bar with `bar.reset()`, args defined below
  <br />
   - show_: show the current state of bar after resetting (default False)

  ## tasks
  you can define a new task with `probarly.Task()` you give it text to display and an id, which is an int used for more efficient task managing, typehint with TaskType an example is below.
  ```python
>>> import probarly
>>> bar = probarly.Progbar(100, {0: probarly.OtherAnimations.morph, "*": probarly.OtherAnimations.up_down})
>>> bar.adv(to=50, task=Task("Part one... ", 0))  # displays the `morph` animation
>>> bar.adv(to=50, task=Task("Part two... ", 99)) # displays the `up_down` animation
  ```

  ## animations
  there are two types: the one that is in the bar, and the one that is after it. the one that is in the bar is just a list of chars, so they don't really need an explanation. an "after-bar" animation is defined with `Animation()`, you give that the frames (list of chars), and slowness (int). typehint with AnimationType

# disclaimers
  - it's bleeding edge, so 60% of the time i just pushed it not even testing =)
  - also, it's a pun on probably, not properly

# installation
```
pip(3) install probarly
```
