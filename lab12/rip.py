import json
import sys


class Router:
    def __init__(self, ip):
        self.ip = ip
        self.neighbors = []
        self.routing_table = {}

    def add_neighbor(self, neighbor_ip, metric):
        self.neighbors.append((neighbor_ip, metric))
        self.routing_table[neighbor_ip] = {"next_hop": neighbor_ip, "metric": metric}

    def update_routing_table(self, received_table, source_ip, step):
        updated = False
        for dest_ip, info in received_table.items():
            new_metric = info["metric"] + self.routing_table[source_ip]["metric"]
            if dest_ip not in self.routing_table or self.routing_table[dest_ip]["metric"] > new_metric:
                self.routing_table[dest_ip] = {"next_hop": source_ip, "metric": new_metric}
                updated = True
        if updated:
            self.log_routing_table(step)
        return updated

    def log_routing_table(self, step):
        sys.stderr.write(f"Simulation step {step} of router {self.ip}\n")
        sys.stderr.write(f"{'Source IP':<20} {'Destination IP':<20} {'Next Hop':<20} {'Metric':<10}\n")
        for dest_ip, info in self.routing_table.items():
            sys.stderr.write(f"{self.ip:<20} {dest_ip:<20} {info['next_hop']:<20} {info['metric']:<10}\n")
        sys.stderr.write("\n")

    def __str__(self):
        result = f"Final state of router {self.ip} table:\n"
        result += f"{'Source IP':<20} {'Destination IP':<20} {'Next Hop':<20} {'Metric':<10}\n"
        for dest_ip, info in self.routing_table.items():
            result += f"{self.ip:<20} {dest_ip:<20} {info['next_hop']:<20} {info['metric']:<10}\n"
        return result


def load_network_from_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    routers = {}
    for router_info in data['routers']:
        router = Router(router_info['ip'])
        routers[router_info['ip']] = router
    for router_info in data['routers']:
        for neighbor in router_info['neighbors']:
            routers[router_info['ip']].add_neighbor(neighbor['ip'], neighbor['metric'])
    return routers


def simulate_rip(routers):
    updated = True
    step = 0
    while updated:
        updated = False
        step += 1
        for router in routers.values():
            for neighbor_ip, _ in router.neighbors:
                neighbor = routers[neighbor_ip]
                if router.update_routing_table(neighbor.routing_table, neighbor_ip, step):
                    updated = True


def main():
    routers = load_network_from_json('network_config.json')
    simulate_rip(routers)
    for router in routers.values():
        print(router)


if __name__ == "__main__":
    main()
