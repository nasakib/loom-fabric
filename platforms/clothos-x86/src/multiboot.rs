//! Multiboot Specification (v1 & v2) Header Definitions & Staging for ClothOS x86/x32 & x86_64
//!
//! Enables GRUB, QEMU (-kernel), and bare-metal bootloaders to load the ClothOS microkernel
//! into memory at 1 MiB physical boundary (0x100000).

pub const MULTIBOOT1_MAGIC: u32 = 0x1BADB002;
pub const MULTIBOOT1_FLAGS: u32 = 0x00000003; // ALIGN (4KB) + MEMINFO
pub const MULTIBOOT1_CHECKSUM: u32 = (0u32).wrapping_sub(MULTIBOOT1_MAGIC + MULTIBOOT1_FLAGS);

pub const MULTIBOOT2_MAGIC: u32 = 0xE85250D6;
pub const MULTIBOOT2_ARCH_I386: u32 = 0;

#[repr(C, align(4))]
pub struct Multiboot1Header {
    pub magic: u32,
    pub flags: u32,
    pub checksum: u32,
}

impl Multiboot1Header {
    pub const fn new() -> Self {
        Self {
            magic: MULTIBOOT1_MAGIC,
            flags: MULTIBOOT1_FLAGS,
            checksum: MULTIBOOT1_CHECKSUM,
        }
    }

    pub fn is_valid(&self) -> bool {
        self.magic == MULTIBOOT1_MAGIC && (self.magic.wrapping_add(self.flags).wrapping_add(self.checksum) == 0)
    }
}

#[derive(Debug, Clone)]
pub struct BootMemoryRegion {
    pub base_addr: u64,
    pub length: u64,
    pub region_type: u32, // 1 = Available RAM, 2 = Reserved, 3 = ACPI Reclaimable
}

#[derive(Debug, Clone)]
pub struct MultibootInfo {
    pub total_memory_kb: u64,
    pub boot_device: u32,
    pub cmdline: String,
    pub memory_regions: Vec<BootMemoryRegion>,
}

impl MultibootInfo {
    pub fn probe_simulated_multiboot() -> Self {
        Self {
            total_memory_kb: 32 * 1024 * 1024, // 32 GB
            boot_device: 0x80,                 // Boot disk
            cmdline: "clothos-x86_64 console=ttyS0 loglevel=debug p0_isolation=enforced".to_string(),
            memory_regions: vec![
                BootMemoryRegion { base_addr: 0x00000000, length: 0x0009FC00, region_type: 1 },
                BootMemoryRegion { base_addr: 0x0009FC00, length: 0x00000400, region_type: 2 },
                BootMemoryRegion { base_addr: 0x000F0000, length: 0x00010000, region_type: 2 },
                BootMemoryRegion { base_addr: 0x00100000, length: 0x7FE00000, region_type: 1 },
            ],
        }
    }
}
