from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

dns = {
    "http://caddy-testbed.com:8080":"http/1.1 without ssl",
    "https://caddy-testbed.com:445":"http/1.1 with ssl",
    "https://caddy-testbed.com:444":"http/2.0",
    "https://caddy-testbed.com":"http/2 + quic/43"
}

with open("./overhead") as f:
    content = f.readlines()

pd.DataFrame().to_dict()
content = [x.strip().split(" ") for x in content]
# content.sort(key=lambda x:x[1])
servers = np.unique(np.array(content)[:, 0])
bitrates = [str(x) for x in sorted(np.unique(np.array(content)[:, 1]).astype(int))]
content = [[(line[0], line[1]), int(line[2])] for line in content]

content = pd.DataFrame(content).groupby(0).median().to_dict()[1]

with open("./bitrate_sizes") as f:
    size_per_rate = f.readlines()
size_per_rate = np.array([x.strip().split(" ") for x in size_per_rate])
size_per_rate = dict(zip(size_per_rate[:, 0], [float(i) for i in size_per_rate[:, 1]]))

fig, ax = plt.subplots()

y_lists = []
for server in servers:
    y = [100.*(content[(server, bitrate)] / size_per_rate[bitrate]-1) for bitrate in bitrates]
    y_lists.append(y)

for i, server in enumerate(servers):
    ax.plot(bitrates, y_lists[i], 'o-',label=dns[server])

half = int(len(bitrates)/2)

#TCP STACK
section = np.ones_like(y_lists[0])*4.70
ax.fill_between(bitrates[:half],0,section[:half],color='0.85')
ax.text(0.25,0.35,r"$\bf{ TCP }$, 32 bytes",transform=ax.transAxes,ha='center',fontsize=8)

section = np.ones_like(y_lists[0])*2.4
ax.fill_between(bitrates[:half],0,section[:half],color='0.92')
ax.text(0.25,0.17,r"$\bf{ IP }$, 20 bytes",transform=ax.transAxes,ha='center',fontsize=8)

section = np.ones_like(y_lists[0])*0.9
ax.fill_between(bitrates[:half],0,section[:half],color='0.98')
ax.text(0.25,0.03,r"$\bf{ ETHERNET }$, 14 bytes",transform=ax.transAxes,ha='center',fontsize=8)

t= ax.text(0.03,0.03,"MTU= 1514 B",transform=ax.transAxes,ha='left',va="bottom",rotation='vertical')
t.set_bbox(dict(facecolor='white', alpha=0.3,edgecolor='white'))

#UDP STACK
section = np.ones_like(y_lists[0])*3.52
ax.fill_between(bitrates[half:],0,section[half:],color='0.85')
ax.text(0.77,0.3,r"$\bf{UDP}$, 8 bytes",transform=ax.transAxes,ha='center',fontsize=8)

section = np.ones_like(y_lists[0])*2.63
ax.fill_between(bitrates[half:],0,section[half:],color='0.92')
ax.text(0.77,0.18,r"$\bf{IP}$, 20 bytes",transform=ax.transAxes,ha='center',fontsize=8)

section = np.ones_like(y_lists[0])*1.08
ax.fill_between(bitrates[half:],0,section[half:],color='0.98')
ax.text(0.77,0.04,r"$\bf{ETHERNET}$, 14 bytes",transform=ax.transAxes,ha='center',fontsize=8)

t= ax.text(0.58,0.03,"MTU = 1295 B",transform=ax.transAxes,ha='left',va="bottom",rotation='vertical')
t.set_bbox(dict(facecolor='white', alpha=0.3,edgecolor='white'))

ax.set_ylabel('overhead [%]')
ax.set_xlabel('bitrate [kBit/s]')

ax.set_title('Caddy Server: '+r"$\bf{Overhead}$"+" "+r"$\bf{analysis}$")
ax.set_xticks(bitrates)
ax.set_xticklabels([str(int(int(x)/1000))for x in bitrates])

ax.legend()
ax.set_ylim(0,10)
ax.set_xlim("100000","4500000")
fig.tight_layout()
plt.show()
