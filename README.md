# IOCP Web Server - Python

## Deskripsi

Repository ini berisi implementasi web server asinkronus sederhana menggunakan Python. Server menggunakan teknik I/O multiplexing dengan `select.select()` untuk menangani multiple koneksi client secara efisien tanpa menggunakan threading. Proyek ini dikembangkan sebagai bagian dari praktikum Network Programming.

## Arsitektur Program

### Komponen Utama

| File | Deskripsi |
|------|-----------|
| `iocp_webserver.py` | Server utama yang menangani koneksi TCP dan HTTP request |
| `index.html` | Halaman web statis yang disajikan kepada client |

### Teknologi yang Digunakan

- **Python 3.x** - Bahasa pemrograman utama
- **Socket Programming** - Komunikasi jaringan level rendah
- **I/O Multiplexing** - Penanganan multiple koneksi dengan `select()`
- **Non-blocking I/O** - Socket dalam mode non-blocking untuk responsivitas tinggi

## Alur Kerja Program

### Diagram Alur Server

```mermaid
flowchart TD
    subgraph INIT["Inisialisasi Server"]
        A1[Buat Socket TCP IPv4] --> A2[Bind ke 127.0.0.1:8080]
        A2 --> A3[Listen - backlog=5]
        A3 --> A4[Set Non-blocking Mode]
        A4 --> A5[Baca index.html]
    end

    INIT --> LOOP

    subgraph LOOP["Event Loop"]
        B1["select.select(clients, [], [])"]
        B1 --> B2{Socket Type?}
    end

    B2 -->|Server Socket| C1[Accept Koneksi Baru]
    B2 -->|Client Socket| D1[Receive Data dari Client]

    subgraph NEW_CONN["Koneksi Baru"]
        C1 --> C2[Set Client Non-blocking]
        C2 --> C3[Tambahkan ke List Clients]
        C3 --> C4[Log: New Connection]
    end

    subgraph HANDLE_DATA["Handle Data Client"]
        D1 --> D2{Data Kosong?}
        D2 -->|Ya| E1[Client Disconnect]
        D2 -->|Tidak| F1[Buat HTTP Response]
        
        E1 --> E2[Hapus dari List Clients]
        E2 --> E3[Tutup Socket]
        
        F1 --> F2[HTTP 200 OK + index.html]
        F2 --> F3[sendall Response ke Client]
        F3 --> F4[Log: Sent index page]
    end

    C4 --> B1
    E3 --> B1
    F4 --> B1

    LOOP -.->|Ctrl+C| SHUTDOWN[Graceful Shutdown]
    SHUTDOWN --> END[Server Closed]
```

### Diagram Interaksi Client-Server

```mermaid
sequenceDiagram
    participant Browser as Client Browser
    participant Server as Python Server

    Note over Server: Server listening on port 8080

    Browser->>Server: TCP Connection Request
    Server-->>Browser: Connection Accepted
    
    Note over Server: Client ditambahkan ke list

    Browser->>Server: HTTP GET Request<br/>GET / HTTP/1.1
    
    Note over Server: Proses request<br/>Baca index.html

    Server-->>Browser: HTTP Response<br/>200 OK<br/>Content-Type: text/html<br/>[index.html content]
    
    Note over Browser: Render halaman web

    alt Client Disconnect
        Browser->>Server: Close Connection
        Note over Server: Hapus client dari list<br/>Tutup socket
    end
```

### Diagram State Socket

```mermaid
stateDiagram-v2
    [*] --> Created: socket.socket()
    Created --> Bound: bind()
    Bound --> Listening: listen()
    Listening --> Accepting: select() readable
    Accepting --> Listening: accept() - add client
    
    state ClientSocket {
        [*] --> Connected: accept()
        Connected --> NonBlocking: setblocking(False)
        NonBlocking --> Readable: select() readable
        Readable --> Processing: recv()
        Processing --> Responding: sendall()
        Responding --> NonBlocking: wait for next request
        Processing --> Closed: empty data
        Closed --> [*]
    }
    
    Listening --> ShutDown: KeyboardInterrupt
    ShutDown --> [*]: close()
```

## Penjelasan Teknis

### I/O Multiplexing dengan select()

Server menggunakan `select.select()` untuk memonitor multiple socket secara bersamaan. Fungsi ini memblokir eksekusi hingga salah satu socket siap untuk operasi I/O.

```python
readable, _, _ = select.select(clients, [], [])
```

Keuntungan pendekatan ini:
- Tidak memerlukan threading atau multiprocessing
- Efisien untuk menangani banyak koneksi bersamaan
- Menghindari busy-waiting dengan blocking pada select()

### Non-blocking Socket

Server socket dan semua client socket dikonfigurasi dalam mode non-blocking:

```python
server_socket.setblocking(False)
client_socket.setblocking(False)
```

Hal ini memungkinkan server untuk tidak terhenti saat menunggu operasi I/O selesai.

### HTTP Response

Server mengirimkan response HTTP yang valid dengan header:
- `HTTP/1.1 200 OK` - Status code sukses
- `Content-Type: text/html` - Tipe konten HTML
- `Content-Length` - Ukuran body response

## Cara Penggunaan

### Prasyarat

- Python 3.x terinstal
- Port 8080 tersedia

### Menjalankan Server

```bash
python iocp_webserver.py
```

### Mengakses Web Page

Buka browser dan akses:
```
http://127.0.0.1:8080
```

### Menghentikan Server

Tekan `Ctrl+C` untuk menghentikan server dengan graceful shutdown.

## Struktur Response HTTP

```
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: [ukuran_file]

[isi index.html]
```

## Limitasi

- Server hanya mendukung metode GET
- Tidak ada routing - semua request akan dilayani dengan index.html
- Koneksi tidak mengimplementasikan keep-alive secara penuh
- Tidak ada penanganan error untuk file index.html yang tidak ditemukan

## Referensi

- [Python Socket Programming](https://docs.python.org/3/library/socket.html)
- [Python select Module](https://docs.python.org/3/library/select.html)
- [HTTP/1.1 Specification](https://www.rfc-editor.org/rfc/rfc2616)
