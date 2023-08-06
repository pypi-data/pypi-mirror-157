# NAME

rplot - stream-based real-time scientific data plotter

![video](https://github.com/h-ohsaki/rplot/blob/master/screenshot/video.gif)

# SYNOPSIS

rplot [-vcW] [-h n[,n...]] [-m #] [-g unit] [-w range] [-F fps]

# DESCRIPTION

This manual page documents **rplot**, a stream-based real-time
scientific data plotter written in Python.  **rplot** reads a stream
of data, which is a series of lines, each of which contains one or
more numeric values.  **rplot** interprets those numbers in the stream
and display a two-dimensional plot for multiple data series
on-the-fly.

**rplot** is a handy tool for visualizing a large amount of scientific
data, which are typically generated from, for instance, an instance of
running computer simulation program.

**rplot** continuously read lines from the standard input.  The format
of the input stream is a simple white-space-separated numeric values.
Each field must be a valid string interpretable by Python's
**float()** function.  Every field may be optionally prefixed by a
label, which is automatically parsed and removed by **rplot**.

One notable features of **rplot** is that it supports both the GUI and
the CUI mode; i.e., visualization on graphic terminals based on PyGame
(built on SDL library) and visualization on text terminals based on
Curses library.  If you prefer to watch the fine details of scientific
data, running **rplot** in the GUI mode is suitable.  On the other
hand, if you prefer to quickly grasp the dynamics of scientific data,
running **rplot** in the CUI mode is a better choice since the CUI
mode runs ultra-fast.

During the visualization, you can tweak the output of **rplot**.  The
current version of **rplot** supports the following commands.

- 0 -- 9

  Turn on and off the selected data series (e.g., pressing 0 toggles
  the display of the first data series).

- Ctrl-a

  Rewind to the beginning of the input stream.

- Ctrl-e

  Display all available data stream, which have been already parsed
  from the standard input.

- Ctrl-f, Ctrl-b

  Change the range of the display window.  Both Ctrl-f and Ctrl-b
  enlarge the current window of the display, but the direction of
  enlargement is different.

- f

  Fill all the time series in different colors.

- q, ESC

  Terminate the **rplot** program.

# OPTIONS

TBD

# INSTALLATION

```sh
$ pip3 install rplot
```

# AVAILABILITY

The latest version of **rplot** is available at PyPI
(https://pypi.org/project/rplot/) .

# AUTHOR

Hiroyuki Ohsaki <ohsaki[atmark]lsnl.jp>
