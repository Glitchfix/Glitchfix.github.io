arr = [
    "Signal Attenuation and Recovery in 5GHz WiFi",
    "Simulating Particle Motion in an Explosion",
    "Golang’s Efficient Garbage Collection Compared to Java",
    "IPC",
    "security features of golang",
    "Quantum Computing in Golang",
    "Exploring eBPF"
]


for fname in arr:
    fname = fname.lower().replace(" ", "-")
    with open(fname+".md", "w") as f:
        f.write("")
    