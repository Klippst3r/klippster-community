//! Klippster WASM converter — ASCII uppercase. Reference implementation of the guest ABI v1.
//!
//! ABI (see https://github.com/Klippst3r/Klippster/blob/main/docs/format-packs/wasm-abi.md):
//!   - export `memory`
//!   - export `buffer_ptr() -> i32`  : offset of a shared buffer in linear memory
//!   - export `buffer_cap() -> i32`  : its capacity in bytes
//!   - export `convert(input_len: i32) -> i32`
//!       The host has written `input_len` bytes at `buffer_ptr()`. Write the result back to the
//!       same buffer and return its length (0..=buffer_cap), or a negative value on error.
//!
//! The exported entry point is named `convert` here; if you rename it, set the matching
//! `options.entrypoint` in klippster.json (it defaults to `convert`).
//!
//! Build: see build.sh. No std, no host imports — the module is fully sandboxed.
#![no_std]

#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! { loop {} }

const CAP: usize = 1 << 16; // 64 KiB
static mut BUFFER: [u8; CAP] = [0; CAP];

#[no_mangle]
pub extern "C" fn buffer_ptr() -> i32 {
    (&raw const BUFFER) as i32
}

#[no_mangle]
pub extern "C" fn buffer_cap() -> i32 {
    CAP as i32
}

#[no_mangle]
pub extern "C" fn convert(input_len: i32) -> i32 {
    if input_len < 0 || input_len as usize > CAP {
        return -1; // malformed request
    }
    let n = input_len as usize;
    let bytes = unsafe { core::slice::from_raw_parts_mut(&raw mut BUFFER as *mut u8, n) };
    let mut i = 0usize;
    while i < n {
        let c = bytes[i];
        if c >= b'a' && c <= b'z' {
            bytes[i] = c - 32;
        }
        i += 1;
    }
    input_len // uppercase preserves length
}
