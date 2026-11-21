# ClothOS Thermodynamic Invariant: Landauer Dissipation Guard
.section .text
.global clothos_read_hardware_joules
clothos_read_hardware_joules:
    rdcycle a0                        # Read hardware cycle counter CSR
    rdinstret a1                      # Read instructions-retired CSR
    rdtime a2                         # Read wall-clock real-time CSR
    # Returns: a0=cycles, a1=instret, a2=walltime
    ret
