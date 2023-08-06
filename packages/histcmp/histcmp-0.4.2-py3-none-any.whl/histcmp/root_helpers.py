from typing import Tuple
import ctypes
import contextlib
import hist
import hist.intervals
import re

import numpy
import ROOT

ROOT.gStyle.SetOptStat(0)


@contextlib.contextmanager
def push_root_level(value):
    prev = ROOT.gErrorIgnoreLevel
    ROOT.gErrorIgnoreLevel = value
    try:
        yield
    finally:
        ROOT.gErrorIgnoreLevel = prev


def integralAndError(item) -> Tuple[float, float]:
    if isinstance(item, ROOT.TH2):
        e = ctypes.c_double(-1)
        i = item.IntegralAndError(
            0, item.GetXaxis().GetNbins(), 0, item.GetYaxis().GetNbins(), e
        )
        return i, e.value
    elif isinstance(item, ROOT.TH1):
        e = ctypes.c_double(-1)
        i = item.IntegralAndError(0, item.GetXaxis().GetNbins(), e)
        return i, e.value
    else:
        raise TypeError(f"Invalid type {type(item)}")


def get_bin_content(item) -> numpy.array:
    if isinstance(item, ROOT.TH2):
        out = numpy.zeros((item.GetXaxis().GetNbins(), item.GetYaxis().GetNbins()))

        for i in range(out.shape[0]):
            for j in range(out.shape[1]):
                out[i][j] = item.GetBinContent(i, j)

        return out
    elif isinstance(item, ROOT.TH1):
        return numpy.array(
            [item.GetBinContent(b) for b in range(1, item.GetXaxis().GetNbins())]
        )
    else:
        raise TypeError("Invalid type")


def get_bin_content_error(item) -> numpy.array:
    if isinstance(item, ROOT.TH2):
        out = numpy.zeros((item.GetXaxis().GetNbins(), item.GetYaxis().GetNbins()))
        err = numpy.zeros((item.GetXaxis().GetNbins(), item.GetYaxis().GetNbins()))

        for i in range(out.shape[0]):
            for j in range(out.shape[1]):
                out[i][j] = item.GetBinContent(i, j)
                err[i][j] = item.GetBinError(i, j)

        return out, err
    elif isinstance(item, ROOT.TH1):
        return (
            numpy.array(
                [
                    item.GetBinContent(b)
                    for b in range(1, item.GetXaxis().GetNbins() + 1)
                ]
            ),
            numpy.array(
                [item.GetBinError(b) for b in range(1, item.GetXaxis().GetNbins() + 1)]
            ),
        )
    else:
        raise TypeError(f"Invalid type {type(item)}")


def _process_axis_title(s):
    def repl(m):
        (o,) = m.groups()
        return "$" + "\\" + o[1:] + "$"

    s = re.sub(r"(#[a-zA-Z]+)", repl, s)
    s = s.replace("\\GT", "\\gt")
    return s


def convert_axis(axis):
    if axis.IsVariableBinSize():
        edges = [axis.GetBinLowEdge(b) for b in range(1, axis.GetNbins() + 1)]
        edges.append(axis.GetBinUpEdge(axis.GetNbins()))
        axis = hist.axis.Variable(edges, name=_process_axis_title(axis.GetTitle()))
        return axis
    else:
        #  print(axis.GetNbins())
        ax = hist.axis.Regular(
            axis.GetNbins(),
            axis.GetBinLowEdge(1),
            axis.GetBinUpEdge(axis.GetNbins()),
            name=_process_axis_title(axis.GetTitle()),
        )
        #  print(ax)
        return ax


def convert_hist(item):
    if isinstance(item, ROOT.TH2):
        h = hist.Hist(
            convert_axis(item.GetXaxis()),
            convert_axis(item.GetYaxis()),
            storage=hist.storage.Weight(),
            name=_process_axis_title(item.GetTitle()),
            label=_process_axis_title(item.GetZaxis().GetTitle()),
        )
        cont, err = get_bin_content_error(item)
        h.view().value = cont
        h.view().variance = err ** 2
        return h
    elif isinstance(item, ROOT.TEfficiency):
        if item.GetDimension() == 1:
            passed = convert_hist(item.GetPassedHistogram())

            eff = passed[:]
            eff.reset()
            eff.name = _process_axis_title(item.GetTitle())

            nbins = item.GetPassedHistogram().GetNbinsX()
            values = numpy.zeros(nbins)
            error = numpy.zeros((2, nbins))
            for b in range(1, nbins + 1):
                values[b - 1] = item.GetEfficiency(b)

                if values[b - 1] != 0:
                    error[1][b - 1] = item.GetEfficiencyErrorUp(b)
                    error[0][b - 1] = item.GetEfficiencyErrorLow(b)

            eff.view().value = values
            eff.view().variance = ((error[0] + error[1]) / 2) ** 2

            return eff, error
        elif item.GetDimension() == 2:
            passed = convert_hist(item.GetPassedHistogram())

            eff = passed.copy()
            eff.reset()
            eff.name = _process_axis_title(item.GetTitle())

            nbins = (
                item.GetPassedHistogram().GetNbinsX(),
                item.GetPassedHistogram().GetNbinsY(),
            )
            values = numpy.zeros(nbins)
            error = numpy.zeros((2, *nbins))
            for x in range(1, nbins[0] + 1):
                for y in range(1, nbins[1] + 1):
                    b = item.GetGlobalBin(x, y)
                    values[x - 1][y - 1] = item.GetEfficiency(b)

                    if values[x - 1][y - 1] != 0:
                        error[1][x - 1][y - 1] = item.GetEfficiencyErrorUp(b)
                        error[0][x - 1][y - 1] = item.GetEfficiencyErrorLow(b)

            eff.view().value = values
            eff.view().variance = ((error[0] + error[1]) / 2) ** 2

            return eff, error
        else:
            raise ValueError(
                f"Too many dimensions for TEfficiency: {item.GetDimension()}"
            )

    elif isinstance(item, ROOT.TH1):
        h = hist.Hist(
            convert_axis(item.GetXaxis()),
            storage=hist.storage.Weight(),
            name=_process_axis_title(item.GetTitle()),
            label=_process_axis_title(item.GetYaxis().GetTitle()),
        )
        cont, err = get_bin_content_error(item)
        h.view().value = cont
        h.view().variance = err ** 2
        return h


def tefficiency_to_th1(eff):
    out = eff.GetPassedHistogram().Clone()
    out.SetDirectory(0)
    out.Reset()

    for b in range(1, out.GetXaxis().GetNbins()):
        out.SetBinContent(b, eff.GetEfficiency(b))
        err = 0.5 * (eff.GetEfficiencyErrorLow(b) + eff.GetEfficiencyErrorUp(b))
        out.SetBinError(b, err)

    return out
