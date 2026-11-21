/* ClothOS Sovereign Microkernel Linker Script for RV64GCV */
OUTPUT_ARCH( "riscv" )
ENTRY( _start )

MEMORY
{
  ram (rwx) : ORIGIN = 0x80200000, LENGTH = 128M
}

SECTIONS
{
  .text.boot : {
    *(.text.boot)
  } > ram

  .text : {
    *(.text .text.*)
  } > ram

  .rodata : {
    *(.rodata .rodata.*)
  } > ram

  .data : {
    *(.data .data.*)
  } > ram

  .bss : {
    __bss_start = .;
    *(.bss .bss.*)
    __bss_end = .;
  } > ram

  _stack_top = ORIGIN(ram) + LENGTH(ram);
}
