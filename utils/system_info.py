import psutil

def get_cpu_usage():
    return psutil.cpu_percent(interval=0.5)

def get_ram_usage():
    return psutil.virtual_memory().percent

def get_network_speed():
    net = psutil.net_io_counters()
    return net.bytes_sent + net.bytes_recv  # total bytes, can calculate delta outside
