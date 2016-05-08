import numpy as np
import pickle


with open('generated_traff.npy', 'r') as outfile:
    generated = np.load(outfile)

time_packets = []

for gen in generated:
    # packets received in 1 sec
    # 1 sec / gen
    # the generated_traff.npy has an array with bytes arrived, so we can
    # easily make as 1500 bytes, for example
    size = int(np.random.choice([64, 1500], 1, [.5, .5]))

    number_of_packets = gen.astype(np.int64) / size

    if number_of_packets == 0:
        seconds = 1.0
    else:
        seconds = (1.0 / number_of_packets)

    if len(time_packets) > 0 and time_packets[-1]["number_of_packets"] == number_of_packets:
        time_packets[-1]["time"] += seconds
    else:
        time_packets += [{
            "time": seconds,
            "number_of_packets": number_of_packets,
            "size": size
        }]

with open("time_gen.p", 'wb') as f:
    pickle.dump(time_packets, f)
