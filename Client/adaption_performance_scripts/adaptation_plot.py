import glob
import json
import os
from collections import OrderedDict, defaultdict
import matplotlib.pyplot as plt
import numpy as np

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

DATA_PATH = 'data'
GRAPH_PATH = '../graphs'

plt.rc('xtick', labelsize=12)
plt.rc('ytick', labelsize=12)

for abr in glob.iglob(DATA_PATH + '/*', recursive=False):
    fig, ax1 = plt.subplots(figsize=(14, 10), dpi=90)
    ax2 = ax1.twinx()

    protocols = glob.iglob(abr + '/*', recursive=False)
    ax1.set_prop_cycle(None)
    bitrates = defaultdict(None)
    bufferLevels = defaultdict(None)
    available = None
    for protocol in protocols:
        bitrates[protocol] = np.empty(1)
        bufferLevels[protocol] = np.empty(1)
        runs_reported = None
        runs_buffer = None
        for filename in glob.iglob(protocol + '/*.json', recursive=True):
            if os.path.isfile(filename):
                with open(filename) as f:
                    test = json.load(f)
                    available = np.array(test["availableBandwidths"]).astype(float)
                    reported = np.array(test["reportedBitrates"]).astype(float)
                    bufferLevel = np.array(test["bufferLevels"]).astype(float)
                    if runs_reported is None or runs_buffer is None:
                        runs_reported = reported
                        runs_buffer = bufferLevel
                    else:
                        if runs_reported is not None or runs_buffer is not None:
                            runs_reported = np.vstack((runs_reported, reported))
                            runs_buffer = np.vstack((runs_buffer, bufferLevel))

        bitrates[protocol] = (np.array(runs_reported))
        bufferLevels[protocol] = (np.array(runs_buffer))

    linestyles = ['-', '--', '-.', ':']
    for i, protocol in enumerate(bitrates.keys()):
        y_bitrates = np.mean(list(bitrates[protocol]), axis=0)
        y_bufferLevels = np.mean(list(bufferLevels[protocol]), axis=0)
        x = range(len(y_bitrates))
        ax1.plot(x, y_bitrates, linewidth=2, linestyle=linestyles[i], label=protocol.split('/')[-1])
        ax2.plot(x, y_bufferLevels, linewidth=0.4)
    ax1.set_prop_cycle(None)
    ax2.set_prop_cycle(None)
    ax1.plot(range(len(available)), available, linewidth=1.5, color="#000000")
    handles, labels = ax1.get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    leg = plt.gcf().legend(by_label.values(), by_label.keys(), loc='upper right', prop={'size': 12})

    fig.text(0.02, 0.5, r"$\bf{bandwidth(black)/bitrate(colored)}$" + " [kBit/s] ", va='center', rotation='vertical',
             fontsize=14)
    fig.text(0.96, 0.5, r"$\bf{buffer\:level(thin)}$" + " [s]", va='center', rotation='-90', fontsize=14)
    fig.text(0.54, 0.04, r"$\bf{time}$" + " [s]", ha='center', fontsize=14)
    fig.subplots_adjust(top=0.85, bottom=0.1, left=0.08, right=0.92)
    fig.suptitle(r"$\bf{Adaptation\:performance}$" + "\n"
                 + r"$\bf{" + abr.split("/")[-1] + "}$"
                 , fontsize=16, y=0.95)

# plt.tight_layout()
# fig.savefig(GRAPH_PATH+'/' + "adaptation_performance" + abr_strategy, transparent=True, dpi=200)
plt.show()
