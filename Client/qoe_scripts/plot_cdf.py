import glob
import json
import os
from collections import OrderedDict
import matplotlib.pyplot as plt
import numpy as np

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

DATA_PATH = '../data/qoe'
GRAPH_PATH = '../graphs'

#TODO AUTOMATION BREAKS THE ORDER OF THE NETWORKS - find more dynamic way to do this
NETWORKS = [["network_16000_0_0", "network_8000_0_0", "network_4000_0_0", "network_2000_0_0", "network_1000_0_0"],
            ["network_16000_50_0", "network_16000_100_0", "network_16000_150_0", "network_16000_200_0",
             "network_16000_250_0"],
            ["network_16000_0_0_5", "network_16000_0_1_5", "network_16000_0_2_5", "network_16000_0_3_5",
             "network_16000_0_4_5"],
            ["network_16000_50_0_5", "network_8000_100_1_5", "network_4000_150_2_5", "network_2000_200_3_5",
             "network_1000_250_4_5"]]

ABR_STRATEGIES = ["abrDynamic"]  # , "abrBola", "abrThroughput"]


def drawCDF(set, xLabel, label, ax, linestyle, marker=None):
    x = np.sort(set)  # Or data.sort(), if data can be modified
    y = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x, y, marker=marker, linestyle=linestyle, label=label)


def plot(X_DESCRIPTOR, Y_DESCRIPTOR, SAMPLE_IDENTIFIER, DTYPE, X_DESCRIPTOR2="", SAMPLE_IDENTIFIER2=None):
    for abr_strategy in ABR_STRATEGIES:

        fig, axes = plt.subplots(ncols=4, nrows=5, sharey='col', sharex='col', subplot_kw=dict(adjustable='box'),
                                 figsize=(14, 8),
                                 squeeze=True)
        fig.text(0.02, 0.5, r"$\bf{" + Y_DESCRIPTOR + "}$", va='center', rotation='vertical', fontsize=10)
        x_text = r"$\bf{" + X_DESCRIPTOR + "}$"
        if X_DESCRIPTOR2 != "":
            x_text = x_text + " / " + X_DESCRIPTOR2
        fig.text(0.54, 0.04, x_text, ha='center', fontsize=10)
        fig.subplots_adjust(top=0.82, bottom=0.1, left=0.07, right=0.996, wspace=.2, hspace=0.3)
        for row in range(4):
            nextplot = [0, 1, 2, 3, 4]
            for network in NETWORKS[row]:

                curAxis = axes[nextplot[0], row]
                for protocol in sorted(
                        [f for f in os.listdir(DATA_PATH + '/' + abr_strategy + '/' + network) if
                         not f.startswith('.')]):
                    averages_per_run = []

                    for test in glob.iglob(DATA_PATH + '/' + abr_strategy + '/' + network + '/' + protocol + '/*.json',
                                           recursive=False):
                        if os.path.isfile(test):
                            with open(test) as f:
                                run = json.load(f)
                                samples = np.array((run[SAMPLE_IDENTIFIER])).astype(DTYPE)
                                averages_per_run.append(np.mean(samples))
                    # cdf
                    averages_per_run = removeOutliers(averages_per_run, 1.3)
                    drawCDF(averages_per_run, X_DESCRIPTOR, protocol, curAxis, '-')
                for ax in fig.get_axes():
                    ax.set_prop_cycle(None)
                if SAMPLE_IDENTIFIER2:
                    for protocol in sorted(
                            [f for f in os.listdir(DATA_PATH + '/' + abr_strategy + '/' + network) if
                             not f.startswith('.')]):
                        averages_per_run = []

                        for test in glob.iglob(
                                                                                        DATA_PATH + '/' + abr_strategy + '/' + network + '/' + protocol + '/*.json',
                                                                                        recursive=False):
                            if os.path.isfile(test):
                                with open(test) as f:
                                    run = json.load(f)
                                    samples = np.array((run[SAMPLE_IDENTIFIER2])).astype(DTYPE)
                                    averages_per_run.append(np.mean(samples))
                        # cdf
                        averages_per_run = removeOutliers(averages_per_run, 1.3)
                        drawCDF(averages_per_run, X_DESCRIPTOR, protocol, curAxis, ':')
                curAxis.set_title(network, fontsize=10)
                handles, labels = curAxis.get_legend_handles_labels()
                by_label = OrderedDict(zip(labels, handles))
                leg = fig.legend(by_label.values(), by_label.keys(), loc='upper right')
                for line in leg.get_lines():
                    line.set_linestyle('-')
                    line.set_linewidth(3)
                nextplot.pop(0)

        title = plt.gcf().suptitle(r"$\bf{" + SAMPLE_IDENTIFIER + "}$"
                                   + "\nnetwork_bandwidth_delay_loss(_loss)"
                                   + "\n" + abr_strategy, fontsize=14)
        title.set_y(0.95)
        title.set_x(0.54)
        fig.savefig(GRAPH_PATH+'/' + SAMPLE_IDENTIFIER + "_" + abr_strategy, transparent=True, dpi=200)


def removeOutliers(x, outlierConstant):
    a = np.array(x)
    upper_quartile = np.percentile(a, 75)
    lower_quartile = np.percentile(a, 25)
    IQR = (upper_quartile - lower_quartile) * outlierConstant
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)

    result = a[np.where((a >= quartileSet[0]) & (a <= quartileSet[1]))]

    return result.tolist()


def plot_rr(X_DESCRIPTOR, Y_DESCRIPTOR, STALL_DURATIONS, STARTUP_TIMES):
    for abr_strategy in ABR_STRATEGIES:

        fig, axes = plt.subplots(ncols=4, nrows=5, sharey='col', sharex='col', subplot_kw=dict(adjustable='box'),
                                 figsize=(14, 8),
                                 squeeze=True)
        fig.text(0.02, 0.5, r"$\bf{" + Y_DESCRIPTOR + "}$", va='center', rotation='vertical', fontsize=10)
        x_text = r"$\bf{" + X_DESCRIPTOR + "}$"
        fig.text(0.54, 0.04, x_text, ha='center', fontsize=10)
        fig.subplots_adjust(top=0.82, bottom=0.1, left=0.07, right=0.996, wspace=.2, hspace=0.3)
        for row in range(4):
            nextplot = [0, 1, 2, 3, 4]
            for network in NETWORKS[row]:

                curAxis = axes[nextplot[0], row]
                for protocol in sorted(
                        [f for f in os.listdir(DATA_PATH + '/' + abr_strategy + '/' + network) if
                         not f.startswith('.')]):
                    rebuffer_rates = []
                    for test in glob.iglob(DATA_PATH + '/' + abr_strategy + '/' + network + '/' + protocol + '/*.json',
                                           recursive=False):
                        if os.path.isfile(test):
                            with open(test) as f:
                                run = json.load(f)
                                samples1 = np.array((run[STALL_DURATIONS])).astype(np.float)
                                try:
                                    _ = (e for e in samples1)
                                    samples1 = sum(samples1)
                                except TypeError:
                                    pass
                                samples2 = np.array((run[STARTUP_TIMES])).astype(np.float)
                                TOTAL = 100.0
                                NOT_PLAYING = TOTAL - samples2 - samples1
                                PLAYING = TOTAL - samples2
                                rebuffer_rates.append(PLAYING / NOT_PLAYING)
                    rebuffer_rates = removeOutliers(rebuffer_rates, 1.3)
                    drawCDF(rebuffer_rates, X_DESCRIPTOR, protocol, curAxis, '-')
                curAxis.set_title(network, fontsize=10)
                handles, labels = curAxis.get_legend_handles_labels()
                by_label = OrderedDict(zip(labels, handles))
                leg = fig.legend(by_label.values(), by_label.keys(), loc='upper right')
                for line in leg.get_lines():
                    line.set_linestyle('-')
                    line.set_linewidth(3)
                nextplot.pop(0)

        title = plt.gcf().suptitle(r"$\bf{" + X_DESCRIPTOR + "}$"
                                   + "\nnetwork_bandwidth_delay_loss(_loss)"
                                   + "\n" + abr_strategy, fontsize=14)
        title.set_y(0.95)
        title.set_x(0.54)
        fig.savefig(GRAPH_PATH+'/' + "rebuffering_ratio_" + abr_strategy, transparent=True, dpi=200)


plot("startUpTime [s]", "CDF", "startUpTime", np.float, SAMPLE_IDENTIFIER2="connectionTime",
     X_DESCRIPTOR2="connectionTime [s]")
plot("Average\:number\:of\:quality\:changes\:[n]", "CDF", "qualityChanges", np.float)
plot("Average\:reported\:birate\:[kBit/s]", "CDF", "reportedBitrates", np.float, SAMPLE_IDENTIFIER2="calculatedBitrates",
     X_DESCRIPTOR2="average calculated Bitrate [kBit/s]")
plot("Average\:number\:of\:stall\:events\:[n]", "CDF", "stallEvents", np.float)
plot_rr("rebuffering\:ratio", "CDF", "stallDurations", "startUpTime")

# plt.show()
