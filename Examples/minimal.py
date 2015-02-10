#!/usr/bin/env python
from plottools import P, doPlot, loadCSV

doPlot('output', {}, [P(data = loadCSV('minimal.csv'))])
