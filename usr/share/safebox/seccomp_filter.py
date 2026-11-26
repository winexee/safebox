#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SafeBox Seccomp BPF Filter Generator

Generates a raw classic BPF seccomp program for Bubblewrap (--seccomp FD)
that denies high-risk kernel/namespace/mount/debug syscalls with EPERM
while allowing normal desktop/browser execution.
"""

import argparse
import ctypes
import errno
import os
import platform
import struct
import sys

SCMP_ACT_ALLOW = 0x7FFF0000
SCMP_ACT_KILL = 0x00000000
SCMP_ACT_ERRNO_EPERM = 0x00050000 | errno.EPERM

BPF_LD_W_ABS = 0x20
BPF_JMP_JEQ_K = 0x15
BPF_JMP_JGE_K = 0x35
BPF_RET_K = 0x06

ARCH_AUDIT = {
    "x86_64": 0xC000003E,
    "amd64": 0xC000003E,
    "aarch64": 0xC00000B7,
    "arm64": 0xC00000B7,
}

# Syscalls denied inside the SafeBox container with -EPERM.
# Returning EPERM (instead of SIGSYS) lets applications probe and fall back gracefully.
DENIED_SYSCALLS = (
    # Nested namespaces & filesystem mount manipulation
    "unshare",
    "setns",
    "mount",
    "umount2",
    "pivot_root",
    "chroot",
    "move_mount",
    "open_tree",
    "fsopen",
    "fsconfig",
    "fsmount",
    "fspick",
    "mount_setattr",
    # Kernel / module / reboot / swap / hardware I/O
    "kexec_load",
    "kexec_file_load",
    "init_module",
    "finit_module",
    "delete_module",
    "reboot",
    "swapon",
    "swapoff",
    "acct",
    "quotactl",
    "quotactl_fd",
    "syslog",
    "vhangup",
    "ioperm",
    "iopl",
    "modify_ldt",
    # High-risk kernel attack surface & cross-process inspection
    "bpf",
    "userfaultfd",
    "io_uring_setup",
    "io_uring_enter",
    "io_uring_register",
    "perf_event_open",
    "lookup_dcookie",
    "open_by_handle_at",
    "name_to_handle_at",
    "add_key",
    "request_key",
    "keyctl",
    "ptrace",
    "process_vm_readv",
    "process_vm_writev",
)

FALLBACK_SYSCALLS = {
    "x86_64": {
        "ptrace": 101,
        "syslog": 103,
        "vhangup": 153,
        "modify_ldt": 154,
        "pivot_root": 155,
        "chroot": 161,
        "acct": 163,
        "mount": 165,
        "umount2": 166,
        "swapon": 167,
        "swapoff": 168,
        "reboot": 169,
        "iopl": 172,
        "ioperm": 173,
        "init_module": 175,
        "delete_module": 176,
        "quotactl": 179,
        "lookup_dcookie": 212,
        "kexec_load": 246,
        "add_key": 248,
        "request_key": 249,
        "keyctl": 250,
        "unshare": 272,
        "perf_event_open": 298,
        "name_to_handle_at": 303,
        "open_by_handle_at": 304,
        "setns": 308,
        "process_vm_readv": 310,
        "process_vm_writev": 311,
        "finit_module": 313,
        "kexec_file_load": 320,
        "bpf": 321,
        "userfaultfd": 323,
        "io_uring_setup": 425,
        "io_uring_enter": 426,
        "io_uring_register": 427,
        "open_tree": 428,
        "move_mount": 429,
        "fsopen": 430,
        "fsconfig": 431,
        "fsmount": 432,
        "fspick": 433,
        "mount_setattr": 442,
        "quotactl_fd": 443,
    },
    "aarch64": {
        "lookup_dcookie": 18,
        "umount2": 39,
        "mount": 40,
        "pivot_root": 41,
        "chroot": 51,
        "vhangup": 58,
        "quotactl": 60,
        "acct": 89,
        "unshare": 97,
        "kexec_load": 104,
        "init_module": 105,
        "delete_module": 106,
        "syslog": 116,
        "ptrace": 117,
        "reboot": 142,
        "add_key": 217,
        "request_key": 218,
        "keyctl": 219,
        "swapon": 224,
        "swapoff": 225,
        "perf_event_open": 241,
        "name_to_handle_at": 264,
        "open_by_handle_at": 265,
        "setns": 268,
        "process_vm_readv": 270,
        "process_vm_writev": 271,
        "finit_module": 273,
        "bpf": 280,
        "userfaultfd": 282,
        "kexec_file_load": 294,
        "io_uring_setup": 425,
        "io_uring_enter": 426,
        "io_uring_register": 427,
        "open_tree": 428,
        "move_mount": 429,
        "fsopen": 430,
        "fsconfig": 431,
        "fsmount": 432,
        "fspick": 433,
        "mount_setattr": 442,
        "quotactl_fd": 443,
    },
}


def _insn(code, jt, jf, k):
    return struct.pack("=HBBI", code, jt, jf, k)


def build_bpf_libseccomp(fd):
    """Export seccomp BPF program directly to file descriptor via libseccomp.so.2."""
    lib = ctypes.CDLL("libseccomp.so.2")
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_rule_add.restype = ctypes.c_int
    lib.seccomp_rule_add.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_int,
        ctypes.c_uint,
    ]
    lib.seccomp_export_bpf.restype = ctypes.c_int
    lib.seccomp_export_bpf.argtypes = [ctypes.c_void_p, ctypes.c_int]

    ctx = lib.seccomp_init(SCMP_ACT_ALLOW)
    if not ctx:
        raise RuntimeError("seccomp_init failed")
    try:
        for name in DENIED_SYSCALLS:
            nr = lib.seccomp_syscall_resolve_name(name.encode("ascii"))
            if nr < 0:
                continue
            rc = lib.seccomp_rule_add(ctx, SCMP_ACT_ERRNO_EPERM, nr, 0)
            if rc != 0:
                raise RuntimeError(f"seccomp_rule_add failed for {name}: {rc}")
        rc = lib.seccomp_export_bpf(ctx, fd)
        if rc != 0:
            raise RuntimeError(f"seccomp_export_bpf failed: {rc}")
    finally:
        lib.seccomp_release(ctx)


def build_bpf_fallback(machine=None):
    """Build raw classic BPF bytes without libseccomp for x86_64 or aarch64."""
    arch = (machine or platform.machine()).lower()
    if arch in ("amd64", "x86_64"):
        arch_key = "x86_64"
    elif arch in ("arm64", "aarch64"):
        arch_key = "aarch64"
    else:
        raise RuntimeError(f"Unsupported architecture for fallback BPF: {arch}")

    table = FALLBACK_SYSCALLS[arch_key]
    nrs = sorted({table[name] for name in DENIED_SYSCALLS if name in table})
    if len(nrs) > 250:
        raise RuntimeError("Too many syscalls for single-byte BPF jump offsets")

    insns = [
        _insn(BPF_LD_W_ABS, 0, 0, 4),                  # A = seccomp_data.arch
        _insn(BPF_JMP_JEQ_K, 1, 0, ARCH_AUDIT[arch_key]),
        _insn(BPF_RET_K, 0, 0, SCMP_ACT_KILL),
        _insn(BPF_LD_W_ABS, 0, 0, 0),                  # A = seccomp_data.nr
    ]

    checks = []
    if arch_key == "x86_64":
        # Block x32 ABI syscalls (nr >= 0x40000000)
        checks.append((BPF_JMP_JGE_K, 0x40000000))
    for nr in nrs:
        checks.append((BPF_JMP_JEQ_K, nr))

    total_checks = len(checks)
    for idx, (op, val) in enumerate(checks):
        # Skip remaining checks + ALLOW instruction to reach DENY at the end
        jt_to_deny = (total_checks - idx - 1) + 1
        insns.append(_insn(op, jt_to_deny, 0, val))

    insns.append(_insn(BPF_RET_K, 0, 0, SCMP_ACT_ALLOW))
    insns.append(_insn(BPF_RET_K, 0, 0, SCMP_ACT_ERRNO_EPERM))
    return b"".join(insns)


def write_bpf_to_path(output_path, force_fallback=False):
    """Write the compiled seccomp BPF filter to output_path."""
    parent = os.path.dirname(os.path.abspath(output_path))
    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(output_path, "wb") as fh:
        if not force_fallback:
            try:
                build_bpf_libseccomp(fh.fileno())
                return "libseccomp"
            except (OSError, RuntimeError):
                fh.seek(0)
                fh.truncate(0)
        data = build_bpf_fallback()
        fh.write(data)
        return "fallback"


def main():
    parser = argparse.ArgumentParser(description="Generate SafeBox Seccomp BPF filter")
    parser.add_argument("-o", "--output", required=True, help="Output BPF file path")
    parser.add_argument("--fallback", action="store_true", help="Force pure-Python BPF fallback")
    args = parser.parse_args()
    try:
        mode = write_bpf_to_path(args.output, force_fallback=args.fallback)
        print(f"seccomp-bpf-ok:{mode}")
    except Exception as exc:
        print(f"seccomp-bpf-error:{exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
