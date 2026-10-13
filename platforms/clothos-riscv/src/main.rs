//! LOOM FABRIC COMMANDER — CLOTHOS RISC-V (`RV64GC` + `RVV 1.0`) SPECIAL EDITION
//!
//! Designed for ClothOS Sovereign Microkernel & RISC-V 64-bit Hardware (`riscv64gc`).
//! Provides:
//! 1. Zero-Terminal Sovereign Boot-to-Prompt Shell (`loom-clothos` / `loom-clothos -p "prompt"`).
//! 2. Hardware PMP (Physical Memory Protection) Enclave for Torque Zero-Trust IP Scrubbing.
//! 3. RVV 1.0 (512-bit Vector Extension) Strip-Mined Layer Allocator across RISC-V Harts + Peer Mesh (`192.168.99.1` & `192.168.99.2`).

mod pmp_enclave;
mod rvv_tensor;

use pmp_enclave::ClothOsPmpEnclave;
use rvv_tensor::RiscvSiliconProfile;
use std::env;
use std::io::{self, Write};
use std::net::{TcpStream, ToSocketAddrs};
use std::time::Duration;

const GATEWAY_HOST: &str = "192.168.99.1:8002";
const HEAD_NODE_HOST: &str = "192.168.99.2:8002";

fn probe_tcp(addr: &str) -> bool {
    if let Ok(mut addrs) = addr.to_socket_addrs() {
        if let Some(sock_addr) = addrs.next() {
            return TcpStream::connect_timeout(&sock_addr, Duration::from_millis(500)).is_ok();
        }
    }
    false
}

fn print_clothos_banner(silicon: &RiscvSiliconProfile, enclave: &ClothOsPmpEnclave) {
    println!("\x1b[38;5;135m================================================================================\x1b[0m");
    println!("\x1b[38;5;48m   LOOM FABRIC COMMANDER // CLOTHOS RISC-V (RV64GC + RVV 1.0) SPECIAL EDITION   \x1b[0m");
    println!("\x1b[38;5;135m================================================================================\x1b[0m");
    println!("  ISA Target     : \x1b[38;5;141m{}\x1b[0m", silicon.isa_string);
    println!(
        "  Compute Harts  : {} Harts | VLEN={}b | Unified Memory={} MB",
        silicon.hart_count, silicon.vlen_bits, silicon.unified_ddr_mb
    );
    println!(
        "  Torque Enclave : PMP Region #{} @ 0x{:08X} ({} KB) [{}]",
        enclave.active_region.index,
        enclave.active_region.base_phys_addr,
        enclave.active_region.size_bytes / 1024,
        enclave.active_region.permissions
    );

    let gw_up = probe_tcp(GATEWAY_HOST) || probe_tcp("127.0.0.1:8002");
    let head_up = probe_tcp(HEAD_NODE_HOST);
    println!(
        "  Mesh Link      : Worker (192.168.99.1) [{}] | Head (192.168.99.2) [{}]",
        if gw_up { "\x1b[32mONLINE\x1b[0m" } else { "\x1b[31mSTANDBY\x1b[0m" },
        if head_up { "\x1b[32mONLINE\x1b[0m" } else { "\x1b[31mSTANDBY\x1b[0m" }
    );
    println!("\x1b[38;5;135m--------------------------------------------------------------------------------\x1b[0m");
}

fn dispatch_prompt(prompt: &str, silicon: &RiscvSiliconProfile, enclave: &mut ClothOsPmpEnclave) {
    let (scrubbed_prompt, was_scrubbed) = enclave.scrub_prompt_in_enclave(prompt);
    let plan = silicon.calculate_rvv_layer_plan(64, 19800);
    println!(
        "\x1b[38;5;141m[ClothOS RVV Triage]\x1b[0m Local RVV Layers: {} | Mesh Layers: {} | Lanes/Hart: {} | PMP Scrubbed: {}",
        plan.local_rvv_layers, plan.peer_mesh_layers, plan.vlen_lanes_per_hart, was_scrubbed
    );
    println!("\x1b[38;5;48mLoom ClothOS ❯\x1b[0m Dispatched payload ({} chars) -> '{}'", scrubbed_prompt.len(), scrubbed_prompt);
}

fn main() {
    let silicon = RiscvSiliconProfile::probe_clothos_silicon();
    let mut enclave = ClothOsPmpEnclave::init_hardware_vault();

    let args: Vec<String> = env::args().collect();
    if args.len() >= 3 && (args[1] == "-p" || args[1] == "--prompt") {
        let prompt = args[2..].join(" ");
        dispatch_prompt(&prompt, &silicon, &mut enclave);
        return;
    }

    print_clothos_banner(&silicon, &enclave);
    println!("Type your prompt directly below (or 'status', 'shard', 'exit'):\n");

    let stdin = io::stdin();
    loop {
        print!("\x1b[38;5;135mClothOS (rv64gc) ❯ \x1b[0m");
        let _ = io::stdout().flush();
        let mut line = String::new();
        if stdin.read_line(&mut line).is_err() {
            break;
        }
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        if trimmed.eq_ignore_ascii_case("exit") || trimmed.eq_ignore_ascii_case("quit") {
            break;
        }
        if trimmed.eq_ignore_ascii_case("status") {
            print_clothos_banner(&silicon, &enclave);
            continue;
        }
        dispatch_prompt(trimmed, &silicon, &mut enclave);
    }
}
