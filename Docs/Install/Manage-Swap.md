# Manage Swap

Swap is space that the kernel uses when physical RAM is full — inactive memory pages are moved to swap so that active applications can stay in RAM.

AnduinOS ships with **Zram enabled by default**: a compressed swap device that lives in RAM itself, using the fast LZ4 algorithm. On a fresh install you already have working swap — no manual setup is needed.

## Manage swap with the GUI

The recommended way to configure swap on AnduinOS is the **Swap Control** application. *(Added in AnduinOS 2.0.1)* It provides a graphical interface for:

* Enabling or disabling the on-disk swap file
* Adjusting the swappiness value
* Configuring Zram size and compression algorithm
* Switching between Zram and Zswap

Launch it from the application menu or run:

```bash
swapcontrol-gtk
```

All changes are applied immediately and survive reboots.

## Check your current swap

```bash title="See active swap devices"
swapon --show
```

```bash title="Memory and swap overview"
free -h
```

If you see `/dev/zram0` in the output, Zram is active. If you also see `/swapfile`, you have an on-disk swap file as a secondary fallback.

## When to disable swap

For most workloads, you should keep swap enabled — the Zram default is designed to improve desktop responsiveness. However, some scenarios call for disabling it:

* **Distributed databases** (e.g. Cassandra, Elasticsearch nodes) where the database engine manages its own memory and OS swap causes unpredictable latency
* **Kubernetes nodes** where the kubelet requires swap to be off
* **Embedded systems** with severe storage constraints

To disable all swap immediately:

```bash title="Disable all swap"
sudo swapoff -a
```

!!! warning "This is temporary"
    Swap devices will return at the next reboot unless you also disable them permanently. Use the **Swap Control** GUI to make permanent changes, or disable the relevant systemd service (`anduinos-zram.service` for Zram).

---

!!! tip "Want to understand the architecture?"

    For a deep dive into Zram, the five-layer swappiness priority system, manual tuning via `sysctl.d`, and what happens when swap-related packages are removed, see the **[Swap Control Strategy](../../Skills/System-Management/Swap-Control-Strategy.md)** article.
